#!/usr/bin/env python3
"""
find-projects-textual: Interactive project finder using Textual TUI

Requires: textual, rich, tomli (if Python <3.11)
"""

import asyncio
from pathlib import Path
from typing import List, Optional, Dict
import os
import sys
import datetime

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Input, DataTable, Static
from textual.containers import Horizontal
from textual.reactive import reactive


# --- Config loading (TOML) ---
def load_config() -> dict:
    config_paths = [
        os.path.expanduser("~/.config/intermcli/find-projects.toml"),
        os.path.expanduser("~/.config/intermcli/config.toml"),
    ]
    config = {}
    for path in config_paths:
        if os.path.exists(path):
            try:
                if sys.version_info >= (3, 11):
                    import tomllib

                    with open(path, "rb") as f:
                        config.update(tomllib.load(f))
                else:
                    import tomli

                    with open(path, "rb") as f:
                        config.update(tomli.load(f))
            except Exception as e:
                print(f"Error loading config {path}: {e}", file=sys.stderr)
    return config


# --- Project type detection ---
DEFAULT_PROJECT_TYPES = {
    "Node.js": ["package.json", "yarn.lock"],
    "Python": ["requirements.txt", "pyproject.toml", "setup.py", "Pipfile"],
    "Rust": ["Cargo.toml"],
    "Go": ["go.mod"],
    "Java": ["pom.xml", "build.gradle", "build.gradle.kts"],
    "PHP": ["composer.json"],
    "Ruby": ["Gemfile", "Gemfile.lock"],
    "C++": ["CMakeLists.txt", "Makefile"],
    "C#": [".csproj", ".sln"],
    "Terraform": ["*.tf", "terraform.tfvars"],
    "Docker": ["Dockerfile", "docker-compose.yml", "docker-compose.yaml"],
    "Kubernetes": ["*.yaml", "*.yml"],
    "Generic": [".git"],
}


def detect_project_type(proj_path: Path, project_types: Dict[str, List[str]]) -> str:
    for ptype, indicators in project_types.items():
        for indicator in indicators:
            if "*" in indicator:
                # Glob match
                if list(proj_path.glob(indicator)):
                    return ptype
            else:
                if (proj_path / indicator).exists():
                    return ptype
    return "Unknown"


# --- Project scanning ---
class Project:
    def __init__(self, name, path, project_type, last_modified):
        self.name = name
        self.path = path
        self.project_type = project_type
        self.last_modified = last_modified


def scan_projects(
    dirs: List[str],
    project_types: Dict[str, List[str]],
    max_depth: int = 3,
    skip_dirs: List[str] = None,
) -> List[Project]:
    """Scan for projects in given dirs, detect type, limit depth, skip heavy dirs."""
    if skip_dirs is None:
        skip_dirs = {
            ".git",
            "node_modules",
            ".venv",
            "venv",
            "__pycache__",
            ".mypy_cache",
            ".pytest_cache",
            "dist",
            "build",
        }
    else:
        skip_dirs = set(skip_dirs)
    projects = []
    seen = set()
    indicators = set()
    for indicators_list in project_types.values():
        indicators.update(indicators_list)
    for base in dirs:
        base_path = Path(base).expanduser()
        if not base_path.exists():
            continue
        for root, dirs_, files in os.walk(base_path):
            rel_depth = len(Path(root).relative_to(base_path).parts)
            # Skip deep directories
            if rel_depth > max_depth:
                dirs_.clear()
                continue
            # Skip heavy/irrelevant directories
            dirs_[:] = [d for d in dirs_ if d not in skip_dirs]
            dir_path = Path(root)
            # Project detection: .git or any indicator file
            if (dir_path / ".git").exists() or any(
                (dir_path / ind).exists() for ind in indicators if "*" not in ind
            ):
                if dir_path in seen:
                    continue
                seen.add(dir_path)
                proj_type = detect_project_type(dir_path, project_types)
                projects.append(
                    Project(
                        name=dir_path.name,
                        path=str(dir_path),
                        project_type=proj_type,
                        last_modified=dir_path.stat().st_mtime,
                    )
                )
    projects.sort(key=lambda p: p.last_modified, reverse=True)
    return projects


def format_time(epoch: float) -> str:
    dt = datetime.datetime.fromtimestamp(epoch)
    return dt.strftime("%Y-%m-%d %H:%M")


# --- Textual App ---


class ProjectTable(DataTable):
    """A DataTable widget for displaying projects."""

    def update_projects(self, projects):
        self.clear()
        self.add_columns("Name", "Type", "Path", "Last Modified")
        for proj in projects:
            self.add_row(
                proj.name, proj.project_type, proj.path, format_time(proj.last_modified)
            )


class FindProjectsTextualApp(App):
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "refresh", "Refresh"),
        ("o", "open_project", "Open Project"),
        ("/", "focus_search", "Search"),
    ]

    search_query = reactive("")
    selected_project = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        config = load_config()
        self.development_dirs = [
            os.path.expanduser(d)
            for d in config.get(
                "development_dirs",
                ["~/development", "~/projects", "~/code", "~/workspace", "~/src"],
            )
        ]
        self.editor = config.get("default_editor", "code")
        self.project_types = config.get("project_types", DEFAULT_PROJECT_TYPES)
        self.projects = []
        self.filtered_projects = []

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield Input(placeholder="Type to search...", id="search")
        yield Horizontal(
            ProjectTable(zebra_stripes=True, id="project_table"),
            Static("Select a project to see details.", id="detail"),
        )

    async def on_mount(self):
        self.search_input = self.query_one("#search", Input)
        self.project_table = self.query_one("#project_table", ProjectTable)
        self.project_detail = self.query_one("#detail", Static)
        await self.refresh_projects()
        self.project_table.focus()

    async def refresh_projects(self):
        self.projects = scan_projects(self.development_dirs, self.project_types)
        self.filtered_projects = self.projects
        self.project_table.update_projects(self.filtered_projects)

    def action_refresh(self):
        asyncio.create_task(self.refresh_projects())

    def action_focus_search(self):
        self.set_focus(self.search_input)

    def on_input_changed(self, event: Input.Changed):
        self.search_query = event.value
        q = self.search_query.lower()
        self.filtered_projects = [
            p
            for p in self.projects
            if q in p.name.lower() or q in p.project_type.lower() or q in p.path.lower()
        ]
        self.project_table.update_projects(self.filtered_projects)

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted):
        idx = event.row_index
        if 0 <= idx < len(self.filtered_projects):
            proj = self.filtered_projects[idx]
            self.selected_project = proj
            self.project_detail.update(
                f"[b]{proj.name}[/b]\n\n"
                f"Type: {proj.project_type}\n"
                f"Path: {proj.path}\n"
                f"Last Modified: {format_time(proj.last_modified)}"
            )

    def action_open_project(self):
        if self.selected_project:
            import subprocess

            try:
                subprocess.Popen([self.editor, self.selected_project.path])
            except Exception as e:
                self.project_detail.update(f"[red]Failed to open: {e}[/red]")
            self.exit()

    def on_data_table_row_selected(self, event: DataTable.RowSelected):
        self.action_open_project()


if __name__ == "__main__":
    FindProjectsTextualApp().run()
