"""The OpenAI embeddings client, against a fake transport shaped like the recorded body."""

from __future__ import annotations

import json
import random
import urllib.error
from pathlib import Path

import pytest

from context_engine.embed import (
    KEY_ENV,
    EmbedAuthError,
    EmbedError,
    OpenAIEmbedder,
    hashed_bow_embedder,
    plan_batches,
)
from context_engine.settings import load_settings

RECORDED = json.loads(
    (Path(__file__).parent / "fixtures/openai_embeddings_response.json").read_text()
)
SECRET = "sk-test-secret-0123456789"
DIM = len(RECORDED["body"]["data"][0]["embedding"])  # the recording cuts vectors to 8 numbers


class FakeService:
    """A transport answering like POST /v1/embeddings: items carry `index`, order is shuffled."""

    def __init__(self, script=None, shuffle=True):
        self.script = list(script or [])
        self.requests: list[dict] = []
        self.headers: list[dict] = []
        self.shuffle = shuffle

    def __call__(self, url, headers, body, timeout):
        payload = json.loads(body)
        self.requests.append({"url": url, **payload})
        self.headers.append(headers)
        if self.script:
            step = self.script.pop(0)
            if isinstance(step, Exception):
                raise step
            status, hdrs, text = step
            if status != 200:
                return status, hdrs, text.encode()
        data = []
        for position, _text in enumerate(payload["input"]):
            item = json.loads(json.dumps(RECORDED["body"]["data"][position % 3]))
            item["embedding"][0] = float(position) + 0.5  # marks which input this vector is for
            item["index"] = position
            data.append(item)
        if self.shuffle:
            random.Random(7).shuffle(data)
        body = {**RECORDED["body"], "data": data, "model": payload["model"]}
        return 200, {}, json.dumps(body).encode()


def make(service, **over):
    """An embedder wired to a fake service, a no-op sleep and a test key."""
    cfg = load_settings()["embedding"]
    cfg.update({"vector_size": DIM, **over})
    sleeps: list[float] = []
    embedder = OpenAIEmbedder.from_settings(
        cfg, transport=service, sleep=sleeps.append, environ={KEY_ENV: SECRET}
    )
    embedder.sleeps = sleeps
    return embedder


def test_request_has_the_recorded_shape():
    service = FakeService()
    make(service)(["alpha", "beta"])
    request = service.requests[0]
    assert request["url"] == "https://api.openai.com/v1/embeddings"
    # The owner's choice (decision 44): the large model, 3072 numbers per vector.
    assert request["model"] == "text-embedding-3-large"
    assert load_settings()["embedding"]["vector_size"] == 3072
    assert request["input"] == ["alpha", "beta"]
    assert request["encoding_format"] == "float"
    assert service.headers[0]["Authorization"] == f"Bearer {SECRET}"


def test_order_is_restored_from_index_when_the_body_is_shuffled():
    service = FakeService(shuffle=True)
    vectors = make(service)([f"text {n}" for n in range(9)])
    assert [v[0] for v in vectors] == [n + 0.5 for n in range(9)]


def test_batches_by_input_count_and_token_budget():
    service = FakeService()
    make(service, request_max_inputs=2)(["a"] * 5)
    assert [len(r["input"]) for r in service.requests] == [2, 2, 1]
    service = FakeService()
    # 300 chars is 100 estimated tokens at 3 chars per token; a budget of 250 fits two
    make(service, request_token_budget=250)(["x" * 300] * 5)
    assert [len(r["input"]) for r in service.requests] == [2, 2, 1]


def test_plan_batches_keeps_order_and_never_drops_an_oversize_item():
    assert plan_batches([10, 10, 500, 10], max_inputs=10, budget=100) == [[0, 1], [2], [3]]


def test_each_input_is_cut_to_the_per_input_cap():
    service = FakeService()
    make(service, input_token_cap=10)(["y" * 1000])
    assert len(service.requests[0]["input"][0]) == 30


def test_retries_429_then_succeeds():
    service = FakeService(script=[(429, {"Retry-After": "2"}, '{"error":{"message":"slow"}}')])
    embedder = make(service)
    assert len(embedder(["a"])) == 1
    assert len(service.requests) == 2
    assert embedder.sleeps and embedder.sleeps[0] >= 2


def test_retries_server_errors_and_network_errors():
    service = FakeService(script=[(503, {}, "{}"), urllib.error.URLError("reset"), (500, {}, "{}")])
    embedder = make(service)
    assert len(embedder(["a"])) == 1
    assert len(service.requests) == 4
    assert len(embedder.sleeps) == 3


def test_gives_up_after_max_retries():
    service = FakeService(script=[(500, {}, "{}")] * 10)
    embedder = make(service, max_retries=2)
    with pytest.raises(EmbedError, match="after 3 attempts"):
        embedder(["a"])


def test_401_raises_without_the_key_and_does_not_retry():
    echo = f'{{"error":{{"message":"Incorrect API key provided: {SECRET}."}}}}'
    service = FakeService(script=[(401, {}, echo)])
    embedder = make(service)
    with pytest.raises(EmbedAuthError) as info:
        embedder(["a"])
    assert SECRET not in str(info.value)
    assert "OPENAI_API_KEY" in str(info.value)
    assert embedder.sleeps == []


def test_other_errors_redact_the_key_from_the_message():
    echo = f'{{"error":{{"message":"bad request near {SECRET}"}}}}'
    service = FakeService(script=[(400, {}, echo)])
    with pytest.raises(EmbedError) as info:
        make(service)(["a"])
    assert SECRET not in str(info.value)
    assert "400" in str(info.value)


def test_missing_key_names_the_variable_only():
    cfg = load_settings()["embedding"]
    embedder = OpenAIEmbedder.from_settings(cfg, transport=FakeService(), environ={})
    with pytest.raises(EmbedError, match="OPENAI_API_KEY is not set"):
        embedder(["a"])


def test_wrong_vector_size_is_an_error():
    with pytest.raises(EmbedError, match="vector size"):
        make(FakeService(), vector_size=DIM + 1)(["a"])


def test_empty_input_list_makes_no_request():
    service = FakeService()
    assert make(service)([]) == []
    assert service.requests == []


def test_hashed_bow_embedder_is_deterministic_and_topical():
    embed = hashed_bow_embedder(64)
    a1, a2, b = embed(["fn compute_total items", "fn compute_total items", "parse the config file"])
    assert a1 == a2 and len(a1) == 64

    def dot(x, y):
        return sum(p * q for p, q in zip(x, y, strict=True))

    near = embed(["compute total of the items"])[0]
    assert dot(near, a1) > dot(near, b)


def test_where_the_key_is_sent_is_fixed_in_code_and_no_settings_or_store_can_move_it():
    # A store sits where the agent can write. Its manifest must not be able to redirect the key.
    from context_engine import embed as embed_module

    cfg = load_settings()["embedding"]
    assert "endpoint" not in cfg and "key_env" not in cfg
    service = FakeService()
    hostile = {**cfg, "vector_size": DIM, "endpoint": "https://evil.example/v1", "key_env": "HOME"}
    embedder = OpenAIEmbedder.from_settings(
        hostile, transport=service, environ={embed_module.KEY_ENV: SECRET, "HOME": "/root"}
    )
    embedder(["text"])
    assert (
        service.requests[0]["url"]
        == embed_module.ENDPOINT
        == "https://api.openai.com/v1/embeddings"
    )
    assert service.headers[0]["Authorization"] == f"Bearer {SECRET}"
