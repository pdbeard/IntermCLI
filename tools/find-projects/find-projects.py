#!/usr/bin/env python3
"""
find-projects: Interactive development project discovery and navigation

Part of the IntermCLI suite - Interactive terminal utilities for developers.
Follows action-target naming convention and progressive enhancement architecture.

Features:
- Core functionality works with Python stdlib only
- Enhanced features with optional dependencies (rich, gitpython)
- Auto-detects project types and provides intelligent sorting
- Integrates with VS Code and other development tools

Usage:
    find-projects [options]
    
Examples:
    find-projects              # Interactive project browser
    find-projects --help       # Show this help
    find-projects --version    # Show version info
    find-projects --config     # Show configuration debug info

Architecture:
    - Progressive enhancement: graceful degradation without optional deps
    - Tool-specific configuration in tools/find-projects/config/
    - Follows IntermCLI design patterns and conventions
"""

import os
import sys
import subprocess
import json
import argparse
from datetime import datetime
from pathlib import Path
from collections import defaultdict

__version__ = "1.0.0"

try:
    import tomllib  # Python 3.11+
except ImportError:
    try:
        import tomli as tomllib  # fallback for older Python
    except ImportError:
        tomllib = None

def load_config():
    """Load configuration with hierarchical precedence"""
    script_dir = Path(__file__).parent
    
    # Try TOML first, fall back to JSON
    toml_config = script_dir / "config" / "defaults.toml"
    json_config = script_dir / "config" / "defaults.json"
    
    # Platform-aware defaults
    home = Path.home()
    
    default_config = {
        'development_dirs': [
            str(home / "development"),
            str(home / "projects"), 
            str(home / "code"),
            str(home / "workspace"),
            str(home / "src"),
            str(home / "git"),
        ],
        'default_editor': 'code',
        'max_scan_depth': 3,
        'skip_dirs': ['.git', 'node_modules', '.vscode', 'dist', 'build', '__pycache__', '.pytest_cache']
    }
    
    # Load tool-specific config
    config_loaded = False
    
    if toml_config.exists() and tomllib:
        try:
            with open(toml_config, 'rb') as f:
                file_config = tomllib.load(f)
                if 'development_dirs' in file_config:
                    file_config['development_dirs'] = [
                        os.path.expanduser(d) for d in file_config['development_dirs']
                    ]
                default_config.update(file_config)
                config_loaded = True
        except Exception as e:
            print(f"⚠️  Warning: Could not load TOML config: {e}")
    
    if not config_loaded and json_config.exists():
        try:
            with open(json_config) as f:
                file_config = json.load(f)
                # Expand tildes in config file paths
                if 'development_dirs' in file_config:
                    file_config['development_dirs'] = [
                        os.path.expanduser(d) for d in file_config['development_dirs']
                    ]
                default_config.update(file_config)
                config_loaded = True
        except Exception as e:
            print(f"⚠️  Warning: Could not load JSON config: {e}")
    
    # Environment variable overrides
    if env_dirs := os.environ.get('FIND_PROJECTS_DIRS'):
        default_config['development_dirs'] = [
            os.path.expanduser(d.strip()) 
            for d in env_dirs.split(':')
        ]
    
    if env_editor := os.environ.get('FIND_PROJECTS_EDITOR'):
        default_config['default_editor'] = env_editor
    
    # Filter to existing directories AFTER all config loading and path expansion
    existing_dirs = [d for d in default_config['development_dirs'] if os.path.exists(d)]
    if existing_dirs:
        default_config['development_dirs'] = existing_dirs
    else:
        print("⚠️  Warning: No configured development directories exist")
        print("Checked directories:")
        for d in default_config['development_dirs']:
            exists = "✅" if os.path.exists(d) else "❌"
            print(f"  {exists} {d}")
    
    return default_config

def debug_config(config):
    """Print configuration debug information"""
    import platform
    print(f"🖥️  Platform: {platform.system()} ({platform.machine()})")
    print(f"🏠 Home directory: {Path.home()}")
    print(f"📁 Current working directory: {Path.cwd()}")
    print(f"🔧 Development directories: {config['development_dirs']}")
    print(f"📝 Default editor: {config['default_editor']}")
    print(f"🔍 Max scan depth: {config['max_scan_depth']}")
    print()

def find_git_projects(config):
    """Find all git repositories in configured directories"""
    projects = []
    
    print("🔍 Scanning directories:")
    for dev_dir in config['development_dirs']:
        print(f"  Checking: {dev_dir}")
        if not os.path.exists(dev_dir):
            print(f"    ❌ Directory doesn't exist")
            continue
        
        print(f"    ✅ Directory exists, scanning...")
        project_count = 0
        
        try:
            for root, dirs, files in os.walk(dev_dir):
                # Limit scan depth
                depth = root[len(dev_dir):].count(os.sep)
                if depth >= config['max_scan_depth']:
                    dirs.clear()
                    continue
                
                # Skip configured directories
                dirs[:] = [d for d in dirs if d not in config['skip_dirs']]
                
                if '.git' in os.listdir(root):
                    project_path = root
                    project_name = os.path.basename(project_path)
                    relative_path = os.path.relpath(project_path, Path.home())
                    
                    print(f"    📁 Found: {project_name} at {relative_path}")
                    
                    # Get last modified time
                    try:
                        last_modified = os.path.getmtime(project_path)
                    except:
                        last_modified = 0
                    
                    # Determine project type
                    project_type = detect_project_type(project_path)
                    
                    projects.append({
                        'name': project_name,
                        'path': project_path,
                        'relative_path': relative_path,
                        'type': project_type,
                        'last_modified': last_modified
                    })
                    
                    project_count += 1
                    
                    # Don't recurse into git repositories
                    dirs.clear()
        
        except Exception as e:
            print(f"    ❌ Error scanning {dev_dir}: {e}")
        
        print(f"    Found {project_count} projects in this directory")
    
    # Sort by last modified (newest first)
    projects.sort(key=lambda x: x['last_modified'], reverse=True)
    print(f"\n📊 Total projects found: {len(projects)}")
    return projects

def detect_project_type(project_path):
    """Detect project type based on files present"""
    try:
        files = os.listdir(project_path)
    except:
        return 'Other'
    
    # Check for specific project markers
    type_markers = {
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
    
    # Check for specific markers first
    for project_type, markers in type_markers.items():
        if any(marker in files for marker in markers):
            return project_type
    
    # Check for file extensions as fallback
    if any(f.endswith('.py') for f in files):
        return 'Python'
    elif any(f.endswith('.js') or f.endswith('.ts') for f in files):
        return 'Node.js'
    elif any(f.endswith('.go') for f in files):
        return 'Go'
    elif any(f.endswith('.php') for f in files):
        return 'PHP'
    elif any(f.endswith('.rb') for f in files):
        return 'Ruby'
    else:
        return 'Other'

def fuzzy_search(query, items, key_func=None):
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
            if text.startswith(query):
                score = 100
            else:
                score = 50
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

def get_type_icon(project_type):
    """Get emoji icon for project type"""
    icons = {
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
    return icons.get(project_type, '📁')

def group_projects_by_type(projects):
    """Group projects by type and return as a flat list with headers"""
    grouped = defaultdict(list)
    
    for project in projects:
        grouped[project['type']].append(project)
    
    # Sort each group by last modified
    for project_type in grouped:
        grouped[project_type].sort(key=lambda x: x['last_modified'], reverse=True)
    
    # Create flat list with type headers
    flat_list = []
    for project_type in sorted(grouped.keys()):
        projects_of_type = grouped[project_type]
        flat_list.append({
            'name': f"{project_type} ({len(projects_of_type)} projects)",
            'path': '',
            'relative_path': '',
            'type': project_type,
            'last_modified': 0,
            'is_header': True
        })
        flat_list.extend(projects_of_type)
    
    return flat_list

def display_projects(projects, selected_index=0, group_by_type=False):
    """Display projects list with selection highlight"""
    os.system('clear')
    
    mode_text = "Grouped by Type" if group_by_type else "Recent Projects"
    print(f"🔍 find-projects - {mode_text}")
    print("=" * 60)
    print(f"Found {len([p for p in projects if not p.get('is_header', False)])} projects\n")
    
    # Show window around selection
    window_size = 15
    start_idx = max(0, selected_index - window_size // 2)
    end_idx = min(len(projects), start_idx + window_size)
    
    if end_idx - start_idx < window_size and start_idx > 0:
        start_idx = max(0, end_idx - window_size)
    
    for i in range(start_idx, end_idx):
        project = projects[i]
        
        if project.get('is_header', False):
            print(f"🏷️  {project['name']}")
            continue
        
        prefix = "► " if i == selected_index else "  "
        type_icon = get_type_icon(project['type'])
        modified_date = datetime.fromtimestamp(project['last_modified']).strftime('%Y-%m-%d')
        
        # Clean up path display
        path_parts = project['relative_path'].split('/')
        if len(path_parts) > 1 and path_parts[0] in ['development', 'projects', 'code']:
            clean_path = '/'.join(path_parts[1:])
        else:
            clean_path = project['relative_path']
        
        if clean_path.endswith('/' + project['name']):
            clean_path = clean_path[:-len('/' + project['name'])]
        
        if group_by_type:
            print(f"   {prefix}• {project['name']} - {clean_path} ({modified_date})")
        else:
            print(f"{prefix}{type_icon} {project['name']} - {clean_path} ({modified_date})")
    
    if len(projects) > window_size:
        print(f"\n... showing {start_idx + 1}-{end_idx} of {len(projects)}")
    
    print("\n" + "─" * 60)
    print("⬆️⬇️  Navigate | Enter: Open | /: Search | t: Toggle Sort | q: Quit")

def open_project(project_path, project_name, editor='code'):
    """Open project in specified editor"""
    try:
        # Change to project directory first
        original_cwd = os.getcwd()
        os.chdir(project_path)
        
        print(f"🚀 Opening {project_name} in {editor}...")
        
        # Just use os.system - it handles everything properly
        exit_code = os.system(f"{editor} .")
        
        # Restore original directory
        os.chdir(original_cwd)
        
        if exit_code == 0:
            print(f"✅ Opened {project_name} in {editor}")
            # Output for shell wrapper to change directory
            print(f"CD_TO:{project_path}")
            return True
        else:
            print(f"❌ Editor exited with code {exit_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error opening project: {e}")
        return False

def get_char():
    """Get single character input (cross-platform)"""
    try:
        import termios, tty
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            char = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return char
    except ImportError:
        # Windows fallback
        import msvcrt
        return msvcrt.getch().decode('utf-8')

def search_mode(all_projects, group_by_type=False):
    """Interactive search mode"""
    query = ""
    original_projects = [p for p in all_projects if not p.get('is_header', False)]
    
    while True:
        filtered_projects = fuzzy_search(
            query, 
            original_projects, 
            key_func=lambda p: f"{p['name']} {p['relative_path']}"
        )
        
        if group_by_type and filtered_projects:
            display_projects_list = group_projects_by_type(filtered_projects)
        else:
            display_projects_list = filtered_projects
        
        os.system('clear')
        search_mode_text = "Search - Grouped" if group_by_type else "Search - Recent"
        print(f"🔍 find-projects - {search_mode_text}")
        print("=" * 60)
        print(f"Query: {query}_")
        print(f"Found {len(filtered_projects)} matches\n")
        
        # Show top results
        count = 0
        for i, project in enumerate(display_projects_list[:15]):
            if project.get('is_header', False):
                print(f"🏷️  {project['name']}")
                continue
            
            count += 1
            type_icon = get_type_icon(project['type'])
            
            path_parts = project['relative_path'].split('/')
            if len(path_parts) > 1 and path_parts[0] in ['development', 'projects', 'code']:
                clean_path = '/'.join(path_parts[1:])
            else:
                clean_path = project['relative_path']
            
            if clean_path.endswith('/' + project['name']):
                clean_path = clean_path[:-len('/' + project['name'])]
            
            if group_by_type:
                print(f"   {count:2d}. • {project['name']} - {clean_path}")
            else:
                print(f"{count:2d}. {type_icon} {project['name']} - {clean_path}")
        
        print("\n" + "─" * 60)
        print("Type to search | Enter: Browse results | Esc: Back | Ctrl+C: Quit")
        
        try:
            char = get_char()
            
            if ord(char) == 27:  # ESC
                return None
            elif ord(char) == 13:  # Enter
                return display_projects_list if display_projects_list else filtered_projects
            elif ord(char) == 127 or ord(char) == 8:  # Backspace
                query = query[:-1]
            elif char.isprintable():
                query += char
                
        except KeyboardInterrupt:
            return None

def get_next_selectable_index(projects, current_index, direction):
    """Find next selectable project (skip headers)"""
    new_index = current_index
    
    while True:
        new_index += direction
        
        if new_index < 0:
            new_index = next((i for i, p in enumerate(projects) if not p.get('is_header', False)), 0)
            break
        elif new_index >= len(projects):
            new_index = next((i for i in range(len(projects)-1, -1, -1) if not projects[i].get('is_header', False)), len(projects) - 1)
            break
        
        if not projects[new_index].get('is_header', False):
            break
    
    return new_index

def main():
    """Main application entry point"""
    parser = argparse.ArgumentParser(
        description='Interactive development project discovery and navigation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  find-projects              Interactive project browser
  find-projects --config     Show configuration information
  find-projects --version    Show version information

Environment Variables:
  FIND_PROJECTS_DIRS         Colon-separated list of directories to scan
  FIND_PROJECTS_EDITOR       Default editor command (default: code)
        '''
    )
    
    parser.add_argument('--version', action='version', version=f'find-projects {__version__}')
    parser.add_argument('--config', action='store_true', help='Show configuration debug info')
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config()
    
    if args.config:
        debug_config(config)
        return
    
    # Find projects
    projects = find_git_projects(config)
    
    if not projects:
        print("\n❌ No git repositories found")
        print("\nTip: Make sure you have git repositories in one of these directories:")
        for dev_dir in config['development_dirs']:
            print(f"  - {dev_dir}")
        print(f"\nOr set FIND_PROJECTS_DIRS environment variable to specify custom directories.")
        return
    
    # Interactive browsing
    group_by_type = False
    current_projects = projects
    selected_index = 0
    
    while True:
        if group_by_type:
            current_projects = group_projects_by_type(projects)
            if selected_index >= len(current_projects) or current_projects[selected_index].get('is_header', False):
                selected_index = next((i for i, p in enumerate(current_projects) if not p.get('is_header', False)), 0)
        else:
            current_projects = projects
            selected_index = min(selected_index, len(current_projects) - 1)
        
        display_projects(current_projects, selected_index, group_by_type)
        
        try:
            char = get_char()
            
            if char == 'q':
                break
            elif char == 't':
                group_by_type = not group_by_type
                continue
            elif char == '/':
                search_results = search_mode(projects, group_by_type)
                if search_results:
                    current_projects = search_results
                    selected_index = next((i for i, p in enumerate(current_projects) if not p.get('is_header', False)), 0)
            elif ord(char) == 13:  # Enter
                if (current_projects and 
                    selected_index < len(current_projects) and 
                    not current_projects[selected_index].get('is_header', False)):
                    project = current_projects[selected_index]
                    if open_project(project['path'], project['name'], config['default_editor']):
                        break
            elif char == '\x1b':  # Arrow keys
                next_chars = sys.stdin.read(2)
                if next_chars == '[A':  # Up arrow
                    if group_by_type:
                        selected_index = get_next_selectable_index(current_projects, selected_index, -1)
                    else:
                        selected_index = max(0, selected_index - 1)
                elif next_chars == '[B':  # Down arrow
                    if group_by_type:
                        selected_index = get_next_selectable_index(current_projects, selected_index, 1)
                    else:
                        selected_index = min(len(current_projects) - 1, selected_index + 1)
            elif char.isdigit():
                # Quick selection by number
                num = int(char)
                selectable_projects = [(i, p) for i, p in enumerate(current_projects) if not p.get('is_header', False)]
                if 1 <= num <= len(selectable_projects):
                    selected_index = selectable_projects[num - 1][0]
                    project = current_projects[selected_index]
                    if open_project(project['path'], project['name'], config['default_editor']):
                        break
                        
        except KeyboardInterrupt:
            break
        except:
            continue
    
    print("\n👋 Goodbye!")

if __name__ == "__main__":
    main()