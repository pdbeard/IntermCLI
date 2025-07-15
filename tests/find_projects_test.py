import os
import tempfile
import shutil
from pathlib import Path
import pytest
import importlib.util

# Dynamically import the find-projects tool as a module
TOOL_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../tools/find-projects/find-projects.py")
)
spec = importlib.util.spec_from_file_location("find_projects", TOOL_PATH)
find_projects = importlib.util.module_from_spec(spec)
spec.loader.exec_module(find_projects)


def test_config_manager_loads_defaults():
    config_manager = find_projects.ConfigManager()
    config = config_manager.load_config()
    assert isinstance(config.development_dirs, list)
    assert config.max_scan_depth > 0


def test_config_manager_env_override(monkeypatch):
    monkeypatch.setenv("FIND_PROJECTS_DIRS", "/tmp:/var")
    monkeypatch.setenv("FIND_PROJECTS_EDITOR", "vim")
    config_manager = find_projects.ConfigManager()
    config = config_manager.load_config()
    assert config.development_dirs == [d for d in ["/tmp", "/var"] if os.path.exists(d)]
    assert config.default_editor == "vim"


def test_project_detector_detects_python(tmp_path):
    # Create a fake Python project
    project_dir = tmp_path / "myproject"
    project_dir.mkdir()
    (project_dir / "requirements.txt").write_text("")
    detector = find_projects.ProjectDetector()
    detected_type = detector.detect_project_type(str(project_dir))
    assert detected_type == "Python"


def test_project_detector_detects_nodejs(tmp_path):
    project_dir = tmp_path / "nodeproj"
    project_dir.mkdir()
    (project_dir / "package.json").write_text("")
    detector = find_projects.ProjectDetector()
    detected_type = detector.detect_project_type(str(project_dir))
    assert detected_type == "Node.js"


def test_project_detector_returns_other_for_empty(tmp_path):
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()
    detector = find_projects.ProjectDetector()
    detected_type = detector.detect_project_type(str(empty_dir))
    assert detected_type == "Other"


def test_security_validator_editor(monkeypatch):
    validator = find_projects.SecurityValidator()
    # Valid editor
    monkeypatch.setenv("PATH", os.environ["PATH"])
    assert validator.validate_editor_command("vim") == "vim"
    # Invalid editor name
    import pytest

    with pytest.raises(ValueError):
        validator.validate_editor_command("invalid editor!")


def test_security_validator_project_path(tmp_path):
    validator = find_projects.SecurityValidator()
    allowed = [str(tmp_path)]
    proj = tmp_path / "proj"
    proj.mkdir()
    assert validator.validate_project_path(str(proj), allowed)
    not_allowed = ["/does/not/exist"]
    assert not validator.validate_project_path(str(proj), not_allowed)


def test_rate_limiter():
    limiter = find_projects.RateLimiter(max_ops_per_second=2)
    assert limiter.check_rate_limit("test")
    assert limiter.check_rate_limit("test")
    # Third call should be rate limited
    assert not limiter.check_rate_limit("test")


def test_search_engine_fuzzy():
    projects = [
        find_projects.Project(
            name="Alpha",
            path="/a",
            relative_path="a",
            project_type="Python",
            last_modified=0,
        ),
        find_projects.Project(
            name="Beta",
            path="/b",
            relative_path="b",
            project_type="Node.js",
            last_modified=0,
        ),
    ]
    results = find_projects.SearchEngine.fuzzy_search(
        "Al", projects, key_func=lambda p: p.name
    )
    assert any(p.name == "Alpha" for p in results)


def test_project_grouper():
    projects = [
        find_projects.Project(
            name="Alpha",
            path="/a",
            relative_path="a",
            project_type="Python",
            last_modified=1,
        ),
        find_projects.Project(
            name="Beta",
            path="/b",
            relative_path="b",
            project_type="Node.js",
            last_modified=2,
        ),
    ]
    grouped = find_projects.ProjectGrouper.group_projects_by_type(projects)
    # Should contain headers and projects
    assert any(p.is_header for p in grouped)
    assert any(p.name == "Alpha" for p in grouped)


def test_project_opener_handles_missing_editor(tmp_path):
    project_dir = tmp_path / "proj"
    project_dir.mkdir()
    # Should fail gracefully
    result = find_projects.ProjectOpener.open_project(
        str(project_dir), "proj", editor="nonexistent_editor"
    )
    assert result is False
