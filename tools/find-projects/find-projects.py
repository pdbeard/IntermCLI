#!/usr/bin/env python3
"""
find-projects: Interactive development project discovery and navigation.
Scan configured directories for git repositories, group and search projects, and open them in your preferred editor.

Part of the IntermCLI suite – interactive terminal utilities for developers and power users.

Example usage:
    find-projects
    find-projects --config
    find-projects --version

Author: pdbeard
"""

import os
import sys
import subprocess
import argparse
from datetime import datetime
from pathlib import Path
import time
from collections import defaultdict
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass
from abc import ABC, abstractmethod

__version__ = "1.0.0"

# TOML support with fallback
try:
    import tomllib  # Python 3.11+
except ImportError:
    try:
        import tomli as tomllib  # fallback for older Python
    except ImportError:
        tomllib = None


@dataclass
class Project:
    """Represents a development project"""
    name: str
    path: str
    relative_path: str
    project_type: str
    last_modified: float
    is_header: bool = False


@dataclass
class Config:
    """Configuration settings"""
    development_dirs: List[str]
    default_editor: str
    max_scan_depth: int
    skip_dirs: List[str]
    max_projects: int
    max_query_length: int
    scan_timeout: int
    allowed_editors: List[str]
    max_file_size: int = 1024 * 1024 


class SecurityValidator:
    """Security validation utilities"""
    
    SECURE_DEFAULTS = {
        'max_scan_depth': 3,
        'max_projects': 1000,
        'max_query_length': 1000,
        'max_file_size': 1024 * 1024,
        'scan_timeout': 30,
        'allowed_editors': ['code', 'vim', 'nvim', 'subl', 'atom'],
        'skip_dirs': [
            '.git', 'node_modules', '.vscode', 'dist', 'build', 
            '__pycache__', '.pytest_cache', '.ssh', '.gnupg'
        ]
    }
    
    @staticmethod
    def validate_editor_command(editor: str) -> str:
        """Validate editor command for security"""
        import shutil
        import re
        
        if not re.match(r'^[a-zA-Z0-9._-]+$', editor):
            raise ValueError(f"Invalid editor command: {editor}")
        
        if not shutil.which(editor):
            raise ValueError(f"Editor not found in PATH: {editor}")
        
        return editor
    
    @staticmethod
    def is_safe_symlink(link_path: str, allowed_dirs: List[str]) -> bool:
        """Check if symlink is safe to follow"""
        try:
            if not os.path.islink(link_path):
                return True
            
            resolved_target = Path(link_path).resolve()
            
            for base_dir in allowed_dirs:
                base_resolved = Path(base_dir).resolve()
                if str(resolved_target).startswith(str(base_resolved)):
                    return True
            
            return False
        except (OSError, RuntimeError, ValueError):
            return False
    
    @staticmethod
    def validate_project_path(path: str, allowed_base_dirs: List[str]) -> bool:
        """Validate that project path is within allowed directories"""
        try:
            resolved_path = Path(path).resolve()
            for base_dir in allowed_base_dirs:
                base_resolved = Path(base_dir).resolve()
                if resolved_path.is_relative_to(base_resolved):
                    return True
            return False
        except:
            return False


class RateLimiter:
    """Rate limiting for file operations"""
    
    def __init__(self, max_ops_per_second: int = 100):
        self.max_ops = max_ops_per_second
        self.operations = defaultdict(list)
    
    def check_rate_limit(self, operation_type: str) -> bool:
        """Check if operation is within rate limit"""
        now = time.time()
        ops = self.operations[operation_type]
        
        # Remove old operations
        ops[:] = [op_time for op_time in ops if now - op_time < 1.0]
        
        if len(ops) >= self.max_ops:
            return False
        
        ops.append(now)
        return True


class ConfigManager:
    """Configuration management"""
    
    def __init__(self):
        self.validator = SecurityValidator()
    
    def load_config(self) -> Config:
        """Load configuration with hierarchical precedence"""
        script_dir = Path(__file__).parent
        config_file = script_dir / "config" / "defaults.toml"
        
        # Platform-aware defaults
        home = Path.home()
        default_dirs = [
            str(home / "development"),
            str(home / "projects"), 
            str(home / "code"),
            str(home / "workspace"),
            str(home / "src"),
            str(home / "git"),
        ]
        
        config_dict = {
            'development_dirs': default_dirs,
            'default_editor': 'vim',
            'max_scan_depth': 3,
            'skip_dirs': ['.git', 'node_modules', '.vscode', 'dist', 'build', '__pycache__', '.pytest_cache'],
            **self.validator.SECURE_DEFAULTS
        }
        
        # Load TOML config if available
        if tomllib and config_file.exists():
            config_dict.update(self._load_toml_config(config_file))
        
        # Environment variable overrides
        self._apply_env_overrides(config_dict)
        
        # Validate and filter
        config_dict['development_dirs'] = self._filter_existing_dirs(config_dict['development_dirs'])
        config_dict['default_editor'] = self._validate_editor(config_dict['default_editor'])
        
        return Config(**config_dict)
    
    def _load_toml_config(self, config_file: Path) -> Dict[str, Any]:
        """Load TOML configuration file"""
        try:
            with open(config_file, 'rb') as f:
                file_config = tomllib.load(f)
                if 'development_dirs' in file_config:
                    file_config['development_dirs'] = [
                        os.path.expanduser(d) for d in file_config['development_dirs']
                    ]
                return file_config
        except Exception as e:
            print(f"⚠️  Warning: Could not load TOML config: {e}")
            return {}
    
    def _apply_env_overrides(self, config_dict: Dict[str, Any]) -> None:
        """Apply environment variable overrides"""
        if env_dirs := os.environ.get('FIND_PROJECTS_DIRS'):
            config_dict['development_dirs'] = [
                os.path.expanduser(d.strip()) 
                for d in env_dirs.split(':')
            ]
        
        if env_editor := os.environ.get('FIND_PROJECTS_EDITOR'):
            config_dict['default_editor'] = env_editor
    
    def _filter_existing_dirs(self, dirs: List[str]) -> List[str]:
        """Filter to existing directories"""
        existing_dirs = [d for d in dirs if os.path.exists(d)]
        if not existing_dirs:
            print("⚠️  Warning: No configured development directories exist")
        return existing_dirs
    
    def _validate_editor(self, editor: str) -> str:
        """Validate editor command"""
        try:
            return self.validator.validate_editor_command(editor)
        except ValueError as e:
            print(f"⚠️  {e}, using 'code' as fallback")
            return 'code'


class ProjectDetector:
    """Project type detection"""
    
    TYPE_MARKERS = {
        'Node.js': ['package.json', 'package-lock.json', 'yarn.lock'],
        'Python': ['requirements.txt', 'pyproject.toml', 'setup.py', 'Pipfile'],
        'Rust': ['Cargo.toml'],
        'Go': ['go.mod', 'go.sum'],
        'Java': ['pom.xml', 'build.gradle', 'build.gradle.kts'],
        'PHP': ['composer.json'],
        'Ruby': ['Gemfile', 'Gemfile.lock'],
        'C++': ['CMakeLists.txt', 'Makefile'],
        'C#': ['.csproj', '.sln'],
    }
    
    TYPE_ICONS = {
        'Node.js': '🟨',
        'Python': '🐍', 
        'Rust': '🦀',
        'Go': '🐹',
        'Java': '☕',
        'PHP': '🐘',
        'Ruby': '💎',
        'C++': '⚙️',
        'C#': '🔷',
        'Other': '📁'
    }
    
    def detect_project_type(self, project_path: str) -> str:
        """Detect project type based on files present"""
        try:
            files = os.listdir(project_path)
        except:
            return 'Other'
        
        # Check for specific project markers
        for project_type, markers in self.TYPE_MARKERS.items():
            if any(marker in files for marker in markers):
                return project_type
        
        # Check for file extensions as fallback
        extension_map = {
            '.py': 'Python',
            '.js': 'Node.js',
            '.ts': 'Node.js',
            '.go': 'Go',
            '.php': 'PHP',
            '.rb': 'Ruby'
        }
        
        for file in files:
            for ext, proj_type in extension_map.items():
                if file.endswith(ext):
                    return proj_type
        
        return 'Other'
    
    def get_type_icon(self, project_type: str) -> str:
        """Get emoji icon for project type"""
        return self.TYPE_ICONS.get(project_type, '📁')


class ProjectScanner:
    """Scans directories for development projects"""
    
    def __init__(self, config: Config):
        self.config = config
        self.detector = ProjectDetector()
        self.validator = SecurityValidator()
        self.rate_limiter = RateLimiter()
    
    def find_git_projects(self) -> List[Project]:
        """Find all git repositories in configured directories"""
        projects = []
        
        print("🔍 Scanning directories:")
        for dev_dir in self.config.development_dirs:
            projects.extend(self._scan_directory(dev_dir))
        
        # Sort by last modified (newest first)
        projects.sort(key=lambda x: x.last_modified, reverse=True)
        print(f"\n📊 Total projects found: {len(projects)}")
        return projects
    
    def _scan_directory(self, dev_dir: str) -> List[Project]:
        """Scan a single directory for projects"""
        print(f"  Checking: {dev_dir}")
        if not os.path.exists(dev_dir):
            print(f"    ❌ Directory doesn't exist")
            return []
        
        print(f"    ✅ Directory exists, scanning...")
        projects = []
        project_count = 0
        
        try:
            for root, dirs, files in os.walk(dev_dir, followlinks=False):
                if not self.rate_limiter.check_rate_limit('file_scan'):
                    time.sleep(0.1)
                    continue
                
                # Security checks
                self._filter_unsafe_symlinks(root, dirs)
                
                # Limit scan depth
                if self._check_depth_limit(root, dev_dir):
                    dirs.clear()
                    continue
                
                # Skip configured directories
                dirs[:] = [d for d in dirs if d not in self.config.skip_dirs]
                
                # Check for git repository
                if '.git' in os.listdir(root):
                    project = self._create_project(root, dev_dir)
                    if project:
                        projects.append(project)
                        project_count += 1
                        dirs.clear()  # Don't recurse into git repositories
        
        except Exception as e:
            print(f"    ❌ Error scanning {dev_dir}: {e}")
        
        print(f"    Found {project_count} projects in this directory")
        return projects
    
    def _filter_unsafe_symlinks(self, root: str, dirs: List[str]) -> None:
        """Remove unsafe symlinks from directory list"""
        for d in dirs[:]:
            dir_path = os.path.join(root, d)
            if os.path.islink(dir_path):
                if not self.validator.is_safe_symlink(dir_path, self.config.development_dirs):
                    print(f"⚠️  Skipping unsafe symlink: {dir_path}")
                    dirs.remove(d)
    
    def _check_depth_limit(self, root: str, dev_dir: str) -> bool:
        """Check if we've exceeded scan depth limit"""
        depth = root[len(dev_dir):].count(os.sep)
        return depth >= self.config.max_scan_depth
    
    def _create_project(self, project_path: str, dev_dir: str) -> Optional[Project]:
        """Create a Project object from a path"""
        if not self.validator.validate_project_path(project_path, self.config.development_dirs):
            print(f"⚠️  Skipping project outside allowed dirs: {project_path}")
            return None
        
        project_name = os.path.basename(project_path)
        relative_path = os.path.relpath(project_path, Path.home())
        
        try:
            last_modified = os.path.getmtime(project_path)
        except:
            last_modified = 0
        
        project_type = self.detector.detect_project_type(project_path)
        
        print(f"    📁 Found: {project_name} at {relative_path}")
        
        return Project(
            name=project_name,
            path=project_path,
            relative_path=relative_path,
            project_type=project_type,
            last_modified=last_modified
        )


class InputHandler:
    """Cross-platform keyboard input handling"""
    
    @staticmethod
    def get_char() -> Optional[str]:
        """Get single character input (cross-platform)"""
        try:
            import termios, tty
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(sys.stdin.fileno())
                char = sys.stdin.read(1)
                
                # Handle Ctrl+C (ASCII 3)
                if ord(char) == 3:  # Ctrl+C
                    raise KeyboardInterrupt()
                
                return char
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        except ImportError:
            # Windows fallback
            import msvcrt
            char = msvcrt.getch().decode('utf-8')
            if ord(char) == 3:  # Ctrl+C on Windows
                raise KeyboardInterrupt()
            return char
        except KeyboardInterrupt:
            # Re-raise KeyboardInterrupt to let it bubble up
            raise
        except:
            return None
    
    @staticmethod
    def is_safe_printable(char: str) -> bool:
        """Check if character is safe for terminal display"""
        if len(char) != 1:
            return False
        
        code = ord(char)
        return 32 <= code <= 126  # Printable ASCII only


class SearchEngine:
    """Fuzzy search implementation"""
    
    @staticmethod
    def fuzzy_search(query: str, items: List[Project], key_func=None) -> List[Project]:
        """Simple fuzzy search implementation"""
        if not query:
            return items
        
        query = query.lower()
        results = []
        
        for item in items:
            text = key_func(item) if key_func else str(item)
            text = text.lower()
            
            # Score based on match quality
            if query in text:
                score = 100 if text.startswith(query) else 50
            else:
                # Character-by-character fuzzy matching
                score = 0
                query_idx = 0
                for char in text:
                    if query_idx < len(query) and char == query[query_idx]:
                        score += 1
                        query_idx += 1
                
                if query_idx == len(query):
                    score += 10
                else:
                    continue
            
            results.append((item, score))
        
        # Sort by score (descending) then by name
        results.sort(key=lambda x: (-x[1], key_func(x[0]) if key_func else str(x[0])))
        return [item for item, score in results]


class ProjectGrouper:
    """Project grouping utilities"""
    
    @staticmethod
    def group_projects_by_type(projects: List[Project]) -> List[Project]:
        """Group projects by type and return as a flat list with headers"""
        grouped = defaultdict(list)
        
        for project in projects:
            grouped[project.project_type].append(project)
        
        # Sort each group by last modified
        for project_type in grouped:
            grouped[project_type].sort(key=lambda x: x.last_modified, reverse=True)
        
        # Create flat list with type headers
        flat_list = []
        for project_type in sorted(grouped.keys()):
            projects_of_type = grouped[project_type]
            flat_list.append(Project(
                name=f"{project_type} ({len(projects_of_type)} projects)",
                path='',
                relative_path='',
                project_type=project_type,
                last_modified=0,
                is_header=True
            ))
            flat_list.extend(projects_of_type)
        
        return flat_list


class ProjectOpener:
    """Handles opening projects in editors"""
    
    @staticmethod
    def open_project(project_path: str, project_name: str, editor: str = 'code') -> bool:
        """Open project in specified editor"""
        try:
            original_cwd = os.getcwd()
            os.chdir(project_path)
            
            print(f"🚀 Opening {project_name} in {editor}...")
            
            result = subprocess.run(
                [editor, "."],
                check=False,
                capture_output=False,
                text=True
            )
            
            os.chdir(original_cwd)
            
            if result.returncode == 0:
                print(f"✅ Opened {project_name} in {editor}")
                print(f"CD_TO:{project_path}")
                return True
            else:
                print(f"❌ Editor exited with code {result.returncode}")
                return False
                
        except FileNotFoundError:
            print(f"❌ Editor '{editor}' not found in PATH")
            return False
        except Exception as e:
            print(f"❌ Error opening project: {e}")
            return False


class UIRenderer:
    """User interface rendering"""
    
    def __init__(self, detector: ProjectDetector):
        self.detector = detector
    
    def display_projects(self, projects: List[Project], selected_index: int = 0, group_by_type: bool = False) -> None:
        """Display projects list with selection highlight"""
        os.system('clear')
        
        mode_text = "Grouped by Type" if group_by_type else "Recent Projects"
        print(f"🔍 find-projects - {mode_text}")
        print("=" * 60)
        print(f"Found {len([p for p in projects if not p.is_header])} projects\n")
        
        # Show window around selection
        window_size = 15
        start_idx = max(0, selected_index - window_size // 2)
        end_idx = min(len(projects), start_idx + window_size)
        
        if end_idx - start_idx < window_size and start_idx > 0:
            start_idx = max(0, end_idx - window_size)
        
        for i in range(start_idx, end_idx):
            self._render_project_line(projects[i], i, selected_index, group_by_type)
        
        if len(projects) > window_size:
            print(f"\n... showing {start_idx + 1}-{end_idx} of {len(projects)}")
        
        print("\n" + "─" * 60)
        print("⬆️⬇️  Navigate | Enter: Open | /: Search | t: Toggle Sort | Ctrl+C: Back")

    def _render_project_line(self, project: Project, index: int, selected_index: int, group_by_type: bool) -> None:
        """Render a single project line"""
        if project.is_header:
            print(f"🏷️  {project.name}")
            return
        
        prefix = "► " if index == selected_index else "  "
        type_icon = self.detector.get_type_icon(project.project_type)
        modified_date = datetime.fromtimestamp(project.last_modified).strftime('%Y-%m-%d')
        
        # Clean up path display
        clean_path = self._clean_path_display(project.relative_path, project.name)
        
        if group_by_type:
            print(f"   {prefix}• {project.name} - {clean_path} ({modified_date})")
        else:
            print(f"{prefix}{type_icon} {project.name} - {clean_path} ({modified_date})")
    
    def _clean_path_display(self, relative_path: str, project_name: str) -> str:
        """Clean up path for display"""
        path_parts = relative_path.split('/')
        if len(path_parts) > 1 and path_parts[0] in ['development', 'projects', 'code']:
            clean_path = '/'.join(path_parts[1:])
        else:
            clean_path = relative_path
        
        if clean_path.endswith('/' + project_name):
            clean_path = clean_path[:-len('/' + project_name)]
        
        return clean_path


class FindProjectsApp:
    """Main application class"""
    
    def __init__(self):
        self.config_manager = ConfigManager()
        self.input_handler = InputHandler()
        self.search_engine = SearchEngine()
        self.grouper = ProjectGrouper()
        self.opener = ProjectOpener()
        self.detector = ProjectDetector()
        self.renderer = UIRenderer(self.detector)
        
        self.config = self.config_manager.load_config()
        self.scanner = ProjectScanner(self.config)
        
        # Add instance variables for state
        self.group_by_type = False
        self.selected_index = 0
    
    def run(self, args) -> None:
        """Main application entry point"""
        if args.config:
            self._debug_config()
            return
        
        projects = self.scanner.find_git_projects()
        
        if not projects:
            self._show_no_projects_message()
            return
        
        self._interactive_browse(projects)
    
    def _debug_config(self) -> None:
        """Print configuration debug information"""
        import platform
        print(f"🖥️  Platform: {platform.system()} ({platform.machine()})")
        print(f"🔧 Development directories: {self.config.development_dirs}")
        print(f"📝 Default editor: {self.config.default_editor}")
        print(f"🔍 Max scan depth: {self.config.max_scan_depth}")
        print(f"🚫 Skip directories: {self.config.skip_dirs}")
        print(f"📋 TOML support: {'✅ Available' if tomllib else '❌ Missing'}")
    
    def _show_no_projects_message(self) -> None:
        """Show message when no projects found"""
        print("\n❌ No git repositories found")
        print("\nTip: Make sure you have git repositories in one of these directories:")
        for dev_dir in self.config.development_dirs:
            print(f"  - {dev_dir}")
        print(f"\nOr set FIND_PROJECTS_DIRS environment variable to specify custom directories.")
    
    def _interactive_browse(self, projects: List[Project]) -> None:
        """Interactive project browsing"""
        current_projects = projects
        
        while True:
            if self.group_by_type:
                current_projects = self.grouper.group_projects_by_type(projects)
                self.selected_index = self._find_next_selectable(current_projects, self.selected_index)
            else:
                current_projects = projects
                self.selected_index = min(self.selected_index, len(current_projects) - 1)
            
            self.renderer.display_projects(current_projects, self.selected_index, self.group_by_type)
            
            try:
                if not self._handle_input(current_projects, projects):
                    break
                    
            except KeyboardInterrupt:
                # In main mode, Ctrl+C immediately quits
                break
    
        print("\n👋 Goodbye!")
    
    def _find_next_selectable(self, projects: List[Project], current_index: int) -> int:
        """Find next selectable project (skip headers)"""
        if current_index >= len(projects) or projects[current_index].is_header:
            return next((i for i, p in enumerate(projects) if not p.is_header), 0)
        return current_index
    
    def _handle_input(self, current_projects: List[Project], all_projects: List[Project]) -> bool:
        """Handle user input - returns False to exit"""
        char = self.input_handler.get_char()
        
        if not char:  # Handle None from get_char()
            return True
            
        if char == 'q':
            return False
        elif char == 't':
            self.group_by_type = not self.group_by_type
            print(f"Debug: Toggled group_by_type to {self.group_by_type}")  # Debug line
        elif char == '/':
            self._handle_search_mode(all_projects)
        elif ord(char) == 13:  # Enter
            self._handle_project_open(current_projects)
        elif char == '\x1b':  # Arrow keys
            self._handle_arrow_keys(current_projects)
        elif char.isdigit():
            self._handle_number_selection(current_projects, char)
        
        return True
    
    def _handle_search_mode(self, projects: List[Project]) -> None:
        """Handle search mode"""
        query = ""
        search_projects = [p for p in projects if not p.is_header]
        search_selected = 0
        
        while True:
            # Filter projects based on query
            if query:
                filtered = self.search_engine.fuzzy_search(
                    query, 
                    search_projects,
                    key_func=lambda p: f"{p.name} {p.relative_path}"
                )
            else:
                filtered = search_projects
            
            # Display search results
            os.system('clear')
            print(f"🔍 Search Mode")
            print("=" * 60)
            print(f"Query: {query}_")
            print(f"Found {len(filtered)} matches\n")
            
            # Show results
            for i, project in enumerate(filtered[:15]):
                prefix = "► " if i == search_selected else "  "
                type_icon = self.detector.get_type_icon(project.project_type)
                print(f"{prefix}{i+1:2d}. {type_icon} {project.name} - {project.relative_path}")
            
            print("\n" + "─" * 60)
            print("Type to search | ⬆️⬇️  Navigate | Enter: Open | Ctrl+C: Back")
            
            # Handle search input - WRAP IN TRY-EXCEPT
            try:
                char = self.input_handler.get_char()
                if not char:
                    continue
                
                if ord(char) == 27:  # Arrow keys
                    try:
                        # Read the next character immediately without timeout
                        next_char1 = sys.stdin.read(1)
                        
                        if next_char1 == '[':
                            # We have an arrow key sequence, read the direction
                            next_char2 = sys.stdin.read(1)
                            
                            if next_char2 == 'A':  # Up arrow
                                search_selected = max(0, search_selected - 1)
                                continue  # IMPORTANT: Stay in search mode
                            elif next_char2 == 'B':  # Down arrow
                                search_selected = min(len(filtered) - 1, search_selected + 1)
                                continue  # IMPORTANT: Stay in search mode
                            else:
                                # Unknown arrow key sequence, ignore
                                continue
                        # If not arrow keys, ignore
                        continue
                    except Exception:
                        # Ignore arrow key errors
                        continue
                        
                elif ord(char) == 13:  # Enter
                    if filtered and search_selected < len(filtered):
                        project = filtered[search_selected]
                        self.opener.open_project(project.path, project.name, self.config.default_editor)
                        break
                elif ord(char) == 127 or ord(char) == 8:  # Backspace
                    query = query[:-1]
                    search_selected = 0
                elif char.isdigit():
                    num = int(char)
                    if 1 <= num <= min(15, len(filtered)):
                        project = filtered[num - 1]
                        self.opener.open_project(project.path, project.name, self.config.default_editor)
                        break
                elif self.input_handler.is_safe_printable(char):
                    query += char
                    search_selected = 0
                    
            except KeyboardInterrupt:
                # Ctrl+C in search mode - go back to main browser
                break
    
    def _handle_project_open(self, projects: List[Project]) -> None:
        """Handle opening a project"""
        if (projects and self.selected_index < len(projects) and 
            not projects[self.selected_index].is_header):
            project = projects[self.selected_index]
            self.opener.open_project(project.path, project.name, self.config.default_editor)
    
    def _handle_arrow_keys(self, projects: List[Project]) -> None:
        """Handle arrow key navigation"""
        try:
            next_char1 = sys.stdin.read(1)
            next_char2 = sys.stdin.read(1)
            
            if next_char1 == '[':
                if next_char2 == 'A':  # Up arrow
                    self.selected_index = self._move_selection_up(projects, self.selected_index)
                elif next_char2 == 'B':  # Down arrow
                    self.selected_index = self._move_selection_down(projects, self.selected_index)
        except:
            pass
    
    def _move_selection_up(self, projects: List[Project], selected_index: int) -> int:
        """Move selection up, skipping headers"""
        new_index = selected_index - 1
        while new_index >= 0 and new_index < len(projects) and projects[new_index].is_header:
            new_index -= 1
        return max(0, new_index)
    
    def _move_selection_down(self, projects: List[Project], selected_index: int) -> int:
        """Move selection down, skipping headers"""
        new_index = selected_index + 1
        while new_index < len(projects) and projects[new_index].is_header:
            new_index += 1
        return min(len(projects) - 1, new_index)
    
    def _handle_number_selection(self, projects: List[Project], char: str) -> None:
        """Handle number-based project selection"""
        num = int(char)
        # Get visible projects (skip headers)
        visible_projects = [(i, p) for i, p in enumerate(projects[:15]) if not p.is_header]
        if 1 <= num <= len(visible_projects):
            project_index, project = visible_projects[num - 1]
            self.opener.open_project(project.path, project.name, self.config.default_editor)


def create_argument_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser"""
    parser = argparse.ArgumentParser(
        description='Interactive development project discovery and navigation with TOML configuration',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  find-projects              Interactive project browser
  find-projects --config     Show configuration information
  find-projects --version    Show version information

Environment Variables:
  FIND_PROJECTS_DIRS         Colon-separated list of directories to scan
  FIND_PROJECTS_EDITOR       Default editor command (default: code)

Configuration:
  Uses TOML configuration file at tools/find-projects/config/defaults.toml
  For Python < 3.11, install tomli: pip install tomli
        '''
    )
    
    parser.add_argument('--version', action='version', version=f'find-projects {__version__}')
    parser.add_argument('--config', action='store_true', help='Show configuration debug info')
    
    return parser


def main():
    """Main entry point"""
    parser = create_argument_parser()
    args = parser.parse_args()
    
    app = FindProjectsApp()
    app.run(args)


if __name__ == "__main__":
    main()