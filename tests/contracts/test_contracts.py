"""Contract tests: schemas, hand-written loaders and the fixtures must all agree."""

from __future__ import annotations

import ast
import copy
import json
import random
import sys
from pathlib import Path

import jsonschema
import pytest

from review_core.contracts import models
from review_core.contracts.models import ContractError

HERE = Path(__file__).parent
FIXTURES = HERE / "fixtures"
CONTRACTS = Path(models.__file__).parent

# Each document kind: schema file, loader name, valid fixture.
KINDS = {
    "findings": ("findings.schema.json", "load_findings", "valid_findings.json"),
    "envelope": ("run_envelope.schema.json", "load_run_envelope", "valid_envelope.json"),
    "key": ("key.schema.json", "load_key", "valid_key.json"),
    "manifest": ("manifest.schema.json", "load_manifest", "valid_manifest.json"),
}

# Keywords a strict structured-output schema may use.
STRICT_KEYWORDS = {
    "$schema",
    "title",
    "description",
    "type",
    "properties",
    "required",
    "additionalProperties",
    "enum",
    "items",
}


def read(path: Path):
    """Parse a JSON file."""
    return json.loads(path.read_text())


def schema(kind: str) -> dict:
    """Load the schema file for a document kind."""
    return read(CONTRACTS / KINDS[kind][0])


def loader(kind: str):
    """Return the models.py loader for a document kind."""
    return getattr(models, KINDS[kind][1])


def strict_violations(node, path="$") -> list[str]:
    """Walk a schema and list every breach of the strict structured-output subset."""
    found = []
    if not isinstance(node, dict):
        return [f"{path}: schema node is not an object"]
    for key in node:
        if key not in STRICT_KEYWORDS:
            found.append(f"{path}: keyword {key!r} is outside the allowed subset")
    types = node.get("type")
    types = types if isinstance(types, list) else [types]
    if "object" in types:
        props = node.get("properties", {})
        if node.get("additionalProperties") is not False:
            found.append(f"{path}: object lacks additionalProperties: false")
        if set(node.get("required", [])) != set(props):
            found.append(f"{path}: required does not list every property")
        for name, sub in props.items():
            found += strict_violations(sub, f"{path}.{name}")
    if "array" in types:
        found += strict_violations(node.get("items"), f"{path}[]")
    return found


@pytest.mark.parametrize("kind", KINDS)
def test_valid_fixture_passes_schema_and_loader(kind):
    doc = read(FIXTURES / KINDS[kind][2])
    jsonschema.validate(doc, schema(kind))
    assert loader(kind)(doc) is not None


@pytest.mark.parametrize("kind", KINDS)
def test_schema_is_itself_a_valid_schema(kind):
    jsonschema.Draft202012Validator.check_schema(schema(kind))


def test_finding_missing_quote_is_rejected():
    doc = read(FIXTURES / "malformed_finding_missing_quote.json")
    with pytest.raises(jsonschema.ValidationError, match="quote"):
        jsonschema.validate(doc, schema("findings"))
    with pytest.raises(ContractError, match="quote"):
        models.load_findings(doc)


def test_finding_with_blank_quote_is_rejected():
    doc = read(FIXTURES / "valid_findings.json")
    doc["findings"][0]["quote"] = "  "
    with pytest.raises(ContractError, match="quote"):
        models.load_findings(doc)


def test_finding_line_end_before_line_start_is_rejected():
    doc = read(FIXTURES / "malformed_finding_line_end_before_start.json")
    jsonschema.validate(doc, schema("findings"))  # a schema cannot compare two fields
    with pytest.raises(ContractError, match="line_end"):
        models.load_findings(doc)


def test_envelope_complete_with_timeout_is_rejected_as_inconsistent():
    doc = read(FIXTURES / "malformed_envelope_complete_with_timeout.json")
    jsonschema.validate(doc, schema("envelope"))
    with pytest.raises(ContractError, match="inconsistent"):
        models.load_run_envelope(doc)


def test_failed_envelope_with_findings_is_rejected():
    doc = read(FIXTURES / "valid_envelope.json")
    doc["envelope"]["status"] = "failed"
    for run in doc["envelope"]["reviewers"]:
        run["outcome"] = "timeout"
        run["findings_count"] = 0
    with pytest.raises(ContractError, match="failed"):
        models.load_run_envelope(doc)


def test_envelope_findings_need_a_fingerprint():
    doc = read(FIXTURES / "valid_envelope.json")
    doc["findings"][0]["fingerprint"] = None
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(doc, schema("envelope"))
    with pytest.raises(ContractError, match="fingerprint"):
        models.load_run_envelope(doc)


def test_key_entry_with_zero_sites_is_rejected():
    doc = read(FIXTURES / "malformed_key_entry_no_sites.json")
    with pytest.raises(jsonschema.ValidationError, match="non-empty|too short"):
        jsonschema.validate(doc, schema("key"))
    with pytest.raises(ContractError, match="sites"):
        models.load_key(doc)


def test_key_round_trips():
    doc = read(FIXTURES / "valid_key.json")
    assert models.key_to_dict(models.load_key(doc)) == doc


def test_key_hash_is_stable_across_key_and_entry_order():
    doc = read(FIXTURES / "valid_key.json")
    shuffled = copy.deepcopy(doc)
    shuffled["entries"].reverse()
    shuffled["entries"][1]["sites"].reverse()
    shuffled = {k: shuffled[k] for k in sorted(shuffled, reverse=True)}
    shuffled["entries"] = [{k: e[k] for k in sorted(e, reverse=True)} for e in shuffled["entries"]]
    random.Random(7).shuffle(shuffled["entries"])
    assert models.key_hash(models.load_key(doc)) == models.key_hash(models.load_key(shuffled))


def test_key_hash_changes_when_an_anchor_changes():
    doc = read(FIXTURES / "valid_key.json")
    edited = copy.deepcopy(doc)
    edited["entries"][0]["sites"][0]["anchor"] = "return total - discount - 1"
    original = models.key_hash(models.load_key(doc))
    assert len(original) == 64
    assert original != models.key_hash(models.load_key(edited))


def test_findings_schema_passes_strict_check():
    assert strict_violations(schema("findings")) == []


def test_strict_check_catches_each_breach():
    good = schema("findings")
    for mutate, expect in (
        (lambda s: s.pop("additionalProperties"), "additionalProperties"),
        (lambda s: s["required"].pop(), "required"),
        (lambda s: s.update(oneOf=[]), "oneOf"),
        (lambda s: s["properties"]["findings"]["items"].update(additionalProperties=True), "[]"),
    ):
        broken = copy.deepcopy(good)
        mutate(broken)
        assert any(expect in v for v in strict_violations(broken)), expect


def test_findings_item_shape_matches_between_findings_and_envelope_schemas():
    reviewer_item = schema("findings")["properties"]["findings"]["items"]
    final_item = schema("envelope")["properties"]["findings"]["items"]
    # The final document adds one field: the other reviewers merged into a finding.
    extra = set(final_item["properties"]) - set(reviewer_item["properties"])
    assert extra == {"also_raised_by"}
    assert set(reviewer_item["properties"]) <= set(final_item["properties"])
    assert final_item["properties"]["fingerprint"]["type"] == "string"
    assert reviewer_item["properties"]["fingerprint"]["type"] == ["string", "null"]


def test_models_imports_only_the_standard_library():
    tree = ast.parse(Path(models.__file__).read_text())
    roots = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots |= {alias.name.split(".")[0] for alias in node.names}
        elif isinstance(node, ast.ImportFrom):
            assert node.level == 0, "relative import in models.py"
            roots.add((node.module or "").split(".")[0])
    assert roots, "models.py imports nothing, so the check proves nothing"
    assert roots <= set(sys.stdlib_module_names), roots - set(sys.stdlib_module_names)


# --- validation that must not pass by accident -----------------------------------------------


def valid(kind: str) -> dict:
    """Return a fresh copy of the valid fixture for a document kind."""
    return copy.deepcopy(read(FIXTURES / KINDS[kind][2]))


def test_complete_envelope_with_no_reviewer_rows_is_rejected():
    doc = valid("envelope")
    doc["envelope"]["reviewers"] = []
    with pytest.raises(ContractError, match="correctness"):
        models.load_run_envelope(doc)


def test_complete_envelope_missing_one_planned_reviewer_is_rejected():
    doc = valid("envelope")
    doc["envelope"]["reviewers"] = doc["envelope"]["reviewers"][:1]
    with pytest.raises(ContractError, match="security"):
        models.load_run_envelope(doc)


def test_envelope_with_two_rows_for_one_reviewer_is_rejected():
    doc = valid("envelope")
    doc["envelope"]["reviewers"].append(dict(doc["envelope"]["reviewers"][0]))
    with pytest.raises(ContractError, match="more than one row"):
        models.load_run_envelope(doc)


def test_envelope_row_for_an_unplanned_reviewer_is_rejected():
    doc = valid("envelope")
    doc["envelope"]["reviewers"].append(
        {"reviewer": "tests", "outcome": "ok", "retries": 0, "findings_count": 0}
    )
    with pytest.raises(ContractError, match="not planned"):
        models.load_run_envelope(doc)


def test_envelope_with_no_planned_reviewers_is_rejected():
    doc = valid("envelope")
    doc["envelope"]["reviewers_planned"] = []
    doc["envelope"]["reviewers"] = []
    with pytest.raises(ContractError, match="reviewers_planned"):
        models.load_run_envelope(doc)


def test_float_that_equals_an_allowed_integer_is_rejected():
    doc = valid("envelope")
    doc["findings"][0]["confidence"] = 75.0
    with pytest.raises(ContractError, match="confidence"):
        models.load_run_envelope(doc)

    key = valid("key")
    key["entries"][0]["tier"] = 1.0
    with pytest.raises(ContractError, match="tier"):
        models.load_key(key)

    findings = valid("findings")
    findings["schema_version"] = 1.0
    with pytest.raises(ContractError, match="schema_version"):
        models.load_findings(findings)


def test_blank_file_and_blank_entry_id_are_rejected():
    doc = valid("findings")
    doc["findings"][0]["file"] = "  "
    with pytest.raises(ContractError, match="file"):
        models.load_findings(doc)

    key = valid("key")
    key["entries"][0]["id"] = ""
    with pytest.raises(ContractError, match="id"):
        models.load_key(key)


def test_read_json_turns_every_unreadable_document_into_a_contract_error(tmp_path):
    not_utf8 = tmp_path / "latin1.json"
    not_utf8.write_bytes(b'{"title": "caf\xe9"}')
    with pytest.raises(ContractError, match="latin1.json"):
        models.read_json(not_utf8)

    too_deep = tmp_path / "deep.json"
    too_deep.write_text("[" * 200_000 + "]" * 200_000)
    with pytest.raises(ContractError, match="deep.json"):
        models.read_json(too_deep)

    not_a_number = tmp_path / "nan.json"
    not_a_number.write_text('{"confidence": NaN}')
    with pytest.raises(ContractError, match="nan.json"):
        models.read_json(not_a_number)


@pytest.mark.parametrize(
    ("path", "expected"),
    [
        ("src/audio.rs", "src/audio.rs"),
        ("./src/audio.rs", "src/audio.rs"),
        ("src/../src/audio.rs", "src/audio.rs"),
        ("/etc/passwd", None),
        ("../outside.rs", None),
        ("src/../../outside.rs", None),
        ("", None),
    ],
)
def test_safe_relpath_keeps_paths_inside_the_tree(path, expected):
    assert models.safe_relpath(path) == expected


def test_final_finding_names_the_other_reviewers_merged_into_it():
    doc = valid("envelope")
    doc["findings"][0]["also_raised_by"] = ["security", "tests"]
    run = models.load_run_envelope(doc)
    assert run.findings[0].also_raised_by == ("security", "tests")

    del doc["findings"][0]["also_raised_by"]
    with pytest.raises(ContractError, match="also_raised_by"):
        models.load_run_envelope(doc)

    doc["findings"][0]["also_raised_by"] = ["nobody"]
    with pytest.raises(ContractError, match="also_raised_by"):
        models.load_run_envelope(doc)


def test_reviewer_document_may_not_carry_also_raised_by():
    doc = valid("findings")
    doc["findings"][0]["also_raised_by"] = []
    with pytest.raises(ContractError, match="also_raised_by"):
        models.load_findings(doc)
    assert models.load_findings(valid("findings")).findings[0].also_raised_by == ()


def test_fingerprint_is_stable_across_reviewers_indentation_and_path_spelling():
    from review_core.envelope import fingerprint

    base = {"file": "src/a.py", "side": "new", "quote": "x = 1\ny = 2", "category": "security"}
    same = [
        {**base, "category": "correctness"},  # who raised it, or under which heading
        {**base, "quote": "\n    x = 1\n        y = 2\n\n"},  # indentation and blank edges
        {**base, "file": "./src/a.py"},  # path spelling
    ]
    assert {fingerprint(f) for f in same} == {fingerprint(base)}
    different = [{**base, "side": "old"}, {**base, "quote": "x = 2"}, {**base, "file": "src/b.py"}]
    assert fingerprint(base) not in {fingerprint(f) for f in different}
    assert len(fingerprint(base)) == 64
