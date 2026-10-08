"""Embedding client for OpenAI's POST /v1/embeddings, written with urllib.

The embedder is passed around
as a plain callable: `texts -> list of vectors`.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import time
import urllib.error
import urllib.request
from collections.abc import Callable, Mapping, Sequence
from typing import Any

from context_engine.tokens import tokenize

Embedder = Callable[[Sequence[str]], list[list[float]]]
Transport = Callable[[str, dict[str, str], bytes, float], tuple[int, dict[str, str], bytes]]


class EmbedError(Exception):
    """The embedding service could not be used; the message never contains the key."""


class EmbedAuthError(EmbedError):
    """The service rejected the key (HTTP 401)."""


def urllib_transport(
    url: str, headers: dict[str, str], body: bytes, timeout: float
) -> tuple[int, dict[str, str], bytes]:
    """POST `body` and return (status, headers, body); network errors propagate."""
    request = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status, dict(response.headers), response.read()
    except urllib.error.HTTPError as err:
        return err.code, dict(err.headers), err.read()


def plan_batches(tokens: Sequence[int], max_inputs: int, budget: int) -> list[list[int]]:
    """Group input positions, in order, so no group exceeds `max_inputs` or `budget` tokens.

    An input over the budget on its own still gets a group of one.
    """
    batches: list[list[int]] = []
    current: list[int] = []
    used = 0
    for position, size in enumerate(tokens):
        if current and (len(current) >= max_inputs or used + size > budget):
            batches.append(current)
            current, used = [], 0
        current.append(position)
        used += size
    if current:
        batches.append(current)
    return batches


# Where the key is sent and which variable holds it are fixed here, in code. They are not
# settings: a store's manifest sits where the agent can write, and must not move the key.
ENDPOINT = "https://api.openai.com/v1/embeddings"
KEY_ENV = "OPENAI_API_KEY"


class OpenAIEmbedder:
    """Callable client: batches inputs, restores order by `index`, retries transient errors."""

    def __init__(
        self,
        model: str,
        vector_size: int,
        chars_per_token: int,
        input_token_cap: int,
        request_max_inputs: int,
        request_token_budget: int,
        max_retries: int,
        backoff_seconds: float,
        backoff_cap_seconds: float,
        timeout_seconds: float,
        transport: Transport | None = None,
        sleep: Callable[[float], None] = time.sleep,
        environ: Mapping[str, str] | None = None,
    ) -> None:
        self.model = model
        self.vector_size = vector_size
        self.key_env = KEY_ENV
        self.endpoint = ENDPOINT
        self.chars_per_token = chars_per_token
        self.input_token_cap = input_token_cap
        self.request_max_inputs = request_max_inputs
        self.request_token_budget = request_token_budget
        self.max_retries = max_retries
        self.backoff_seconds = backoff_seconds
        self.backoff_cap_seconds = backoff_cap_seconds
        self.timeout_seconds = timeout_seconds
        self._transport = transport or urllib_transport
        self._sleep = sleep
        self._environ = os.environ if environ is None else environ
        self.requests = 0
        self.tokens = 0

    @classmethod
    def from_settings(cls, cfg: Mapping[str, Any], **kwargs: Any) -> OpenAIEmbedder:
        """Build from the `embedding` table of the settings (or of a manifest).

        Only the named tunables are read; anything else in the table is ignored.
        """
        names = (
            "model vector_size chars_per_token input_token_cap "
            "request_max_inputs request_token_budget max_retries backoff_seconds "
            "backoff_cap_seconds timeout_seconds"
        ).split()
        return cls(**{name: cfg[name] for name in names}, **kwargs)

    def __call__(self, texts: Sequence[str]) -> list[list[float]]:
        """Embed `texts`; the result is in the same order, one vector per text."""
        cap = self.input_token_cap * self.chars_per_token
        inputs = [(text[:cap] or " ") for text in texts]
        sizes = [max(1, -(-len(text) // self.chars_per_token)) for text in inputs]
        out: list[list[float] | None] = [None] * len(inputs)
        for batch in plan_batches(sizes, self.request_max_inputs, self.request_token_budget):
            vectors = self._request([inputs[i] for i in batch])
            for offset, position in enumerate(batch):
                out[position] = vectors[offset]
        return [vector for vector in out if vector is not None]

    def _key(self) -> str:
        """The API key from the environment, read at call time."""
        key = self._environ.get(self.key_env)
        if not key:
            raise EmbedError(f"environment variable {self.key_env} is not set")
        return key

    def _request(self, batch: list[str]) -> list[list[float]]:
        """One embeddings request with retries; returns vectors in `batch` order."""
        key = self._key()
        body = json.dumps(
            {"model": self.model, "input": batch, "encoding_format": "float"}
        ).encode()
        headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
        last = ""
        attempts = self.max_retries + 1
        for attempt in range(attempts):
            retry_after = 0.0
            try:
                status, reply, payload = self._transport(
                    self.endpoint, headers, body, self.timeout_seconds
                )
            except OSError as exc:  # URLError, timeouts and resets are all OSError
                last = f"network error: {type(exc).__name__}"
            else:
                self.requests += 1
                if status == 200:
                    return self._parse(payload, len(batch))
                if status == 401:
                    raise EmbedAuthError(
                        f"the embedding service rejected the key in {self.key_env} (HTTP 401)"
                    )
                if status != 429 and status < 500:
                    raise EmbedError(f"HTTP {status}: {self._message(payload, key)}")
                last = f"HTTP {status}"
                retry_after = _retry_after(reply)
            if attempt + 1 < attempts:
                delay = min(self.backoff_cap_seconds, self.backoff_seconds * 2**attempt)
                self._sleep(min(self.backoff_cap_seconds, max(delay, retry_after)))
        raise EmbedError(f"embedding request failed after {attempts} attempts: {last}")

    @staticmethod
    def _message(payload: bytes, key: str) -> str:
        """The service's error message with the key removed, or a short fallback."""
        try:
            message = str(json.loads(payload)["error"]["message"])
        except (ValueError, KeyError, TypeError):
            message = "no error message"
        return message.replace(key, "***")[:300]

    def _parse(self, payload: bytes, count: int) -> list[list[float]]:
        """Vectors from a 200 body, put back in input order by each item's `index`."""
        try:
            body = json.loads(payload)
            items = body["data"]
            slots: dict[int, list[float]] = {}
            for item in items:
                slots[int(item["index"])] = [float(x) for x in item["embedding"]]
            self.tokens += int(body.get("usage", {}).get("total_tokens", 0))
        except (ValueError, KeyError, TypeError) as exc:
            raise EmbedError(f"unexpected embeddings response: {type(exc).__name__}") from None
        if sorted(slots) != list(range(count)):
            raise EmbedError(f"embeddings response has {len(slots)} items for {count} inputs")
        vectors = [slots[i] for i in range(count)]
        if any(len(v) != self.vector_size for v in vectors):
            raise EmbedError(
                f"vector size {len(vectors[0])} does not match the configured {self.vector_size}"
            )
        return vectors


def _retry_after(headers: Mapping[str, str]) -> float:
    """Seconds from a Retry-After header, or 0."""
    for name, value in headers.items():
        if name.lower() == "retry-after":
            try:
                return max(0.0, float(value))
            except ValueError:
                return 0.0
    return 0.0


def hashed_bow_embedder(vector_size: int) -> Embedder:
    """A deterministic offline embedder: hashed bag of words. Used only as model "fake"."""

    def embed(texts: Sequence[str]) -> list[list[float]]:
        """One signed hashed term-frequency vector per text."""
        out = []
        for text in texts:
            counts: dict[str, int] = {}
            for token in tokenize(text):
                counts[token] = counts.get(token, 0) + 1
            vector = [0.0] * vector_size
            for token, n in counts.items():
                digest = hashlib.sha256(token.encode()).digest()
                slot = int.from_bytes(digest[:4], "little") % vector_size
                sign = 1.0 if digest[4] & 1 else -1.0
                vector[slot] += sign * (1.0 + math.log(n))
            out.append(vector)
        return out

    return embed
