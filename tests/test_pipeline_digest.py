"""The pipeline digest: any change to a pipeline file moves it; caches, docs and analysis do not."""

from pathlib import Path

from review_core.pipeline_digest import load_config, pipeline_digest

CONFIG = """include = ["src/tool/**", "rows.toml"]
exclude_names = ["__pycache__", ".DS_Store"]
exclude_suffixes = [".pyc"]
exclude_paths = ["src/tool/analysis.py"]
"""


def make_tree(root: Path) -> Path:
    (root / "src" / "tool").mkdir(parents=True)
    (root / "src" / "tool" / "a.py").write_text("x = 1\n")
    (root / "src" / "tool" / "analysis.py").write_text("y = 1\n")
    (root / "rows.toml").write_text("w = 1\n")
    (root / "README.md").write_text("hi\n")
    config = root / "pipeline.toml"
    config.write_text(CONFIG)
    return config


def test_any_change_to_a_pipeline_file_moves_the_digest(tmp_path):
    config = make_tree(tmp_path)
    seen = {pipeline_digest(tmp_path, config)}
    (tmp_path / "src" / "tool" / "a.py").write_text("x = 2\n")
    seen.add(pipeline_digest(tmp_path, config))
    (tmp_path / "rows.toml").write_text("w = 2\n")
    seen.add(pipeline_digest(tmp_path, config))
    (tmp_path / "src" / "tool" / "b.py").write_text("")
    seen.add(pipeline_digest(tmp_path, config))
    (tmp_path / "src" / "tool" / "b.py").rename(tmp_path / "src" / "tool" / "c.py")
    seen.add(pipeline_digest(tmp_path, config))
    assert len(seen) == 5


def test_caches_docs_and_analysis_code_leave_it_alone(tmp_path):
    config = make_tree(tmp_path)
    before = pipeline_digest(tmp_path, config)
    cache = tmp_path / "src" / "tool" / "__pycache__"
    cache.mkdir()
    (cache / "a.cpython-313.pyc").write_bytes(b"\0")
    (tmp_path / "src" / "tool" / ".DS_Store").write_bytes(b"\0")
    (tmp_path / "src" / "tool" / "analysis.py").write_text("y = 2\n")
    (tmp_path / "README.md").write_text("changed\n")
    assert pipeline_digest(tmp_path, config) == before


def test_this_repository_covers_the_tool_the_skills_and_the_evals():
    config = load_config()
    for pattern in ("src/review_core/**", "src/context_engine/**", "src/plugin/**", "evals/**"):
        assert pattern in config["include"]

    digest = pipeline_digest()
    assert len(digest) == 64 and digest == pipeline_digest()
