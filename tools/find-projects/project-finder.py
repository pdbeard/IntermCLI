#!/usr/bin/env python3

import os
import sys
import subprocess
import json
from datetime import datetime
from pathlib import Path
from collections import defaultdict

def load_config():
    """Load configuration from config file"""
    script_dir = Path(__file__).parent.parent
    config_file = script_dir / "config" / "defaults.conf"
    
    # Platform-aware default configuration
    home = os.path.expanduser("~")
    
    # Common development directory patterns for both macOS and Linux
    default_dirs = [
        f"{home}/development",
        f"{home}/projects", 
        f"{home}/code",
        f"{home}/workspace",  # Common on Linux
        f"{home}/src",        # Common on Linux
        f"{home}/git",        # Alternative pattern
    ]
    
    # Filter to only existing directories for defaults
    existing_dirs = [d for d in default_dirs if os.path.exists(d)]
    
    config = {
        'DEVELOPMENT_DIRS': existing_dirs if existing_dirs else default_dirs[:3],
        'DEFAULT_EDITOR': 'code'
    }
    
    # Override with config file if it exists
    if config_file.exists():
        try:
            with open(config_file) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip('"')
                        
                        if key == 'PF_DEVELOPMENT_DIRS':
                            # Expand environment variables like $HOME
                            value = os.path.expandvars(value)
                            config['DEVELOPMENT_DIRS'] = [
                                os.path.expanduser(d.strip()) 
                                for d in value.split(':')
                            ]
                        elif key == 'PF_DEFAULT_EDITOR':
                            config['DEFAULT_EDITOR'] = value
        except Exception as e:
            print(f"⚠️  Warning: Could not load config file: {e}")
    
    return config

# Load configuration at module level
CONFIG = load_config()
DEVELOPMENT_DIRS = CONFIG['DEVELOPMENT_DIRS']

def debug_config():
    """Print configuration debug information"""
    import platform
    print(f"🖥️  Platform: {platform.system()} ({platform.machine()})")
    print(f"🏠 Home directory: {os.path.expanduser('~')}")
    print(f"📁 Current working directory: {os.getcwd()}")
    print(f"🔧 Config directories: {CONFIG['DEVELOPMENT_DIRS']}")
    print(f"📝 Default editor: {CONFIG['DEFAULT_EDITOR']}")
    print()

def find_git_projects():
    """Find all git repositories in development directories"""
    projects = []
    
    print("🔍 Scanning directories:")
    for dev_dir in DEVELOPMENT_DIRS:
        print(f"  Checking: {dev_dir}")
        if not os.path.exists(dev_dir):
            print(f"    ❌ Directory doesn't exist")
            continue
        
        print(f"    ✅ Directory exists, scanning...")
        project_count = 0
        
        try:
            for root, dirs, files in os.walk(dev_dir):
                # Skip common non-project directories
                dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', '.vscode', 'dist', 'build', '__pycache__']]
                
                if '.git' in os.listdir(root):
                    project_path = root
                    project_name = os.path.basename(project_path)
                    relative_path = os.path.relpath(project_path, os.path.expanduser("~"))
                    
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
                    if '.git' in dirs:
                        dirs.remove('.git')
        
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
    
    if 'package.json' in files:
        return 'Node.js'
    elif any(f.endswith('.py') for f in files) or 'requirements.txt' in files or 'pyproject.toml' in files:
        return 'Python'
    elif 'Cargo.toml' in files:
        return 'Rust'
    elif 'go.mod' in files or any(f.endswith('.go') for f in files):
        return 'Go'
    elif 'pom.xml' in files or 'build.gradle' in files:
        return 'Java'
    elif 'composer.json' in files or any(f.endswith('.php') for f in files):
        return 'PHP'
    elif 'Gemfile' in files or any(f.endswith('.rb') for f in files):
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
        
        # Exact match gets highest score
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
                score += 10  # All characters found
            else:
                continue  # Skip if not all characters found
        
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
        'Other': '📁'
    }
    return icons.get(project_type, '📁')

def group_projects_by_type(projects):
    """Group projects by type and return as a flat list with headers"""
    grouped = defaultdict(list)
    
    # Group projects by type
    for project in projects:
        grouped[project['type']].append(project)
    
    # Sort each group by last modified (newest first)
    for project_type in grouped:
        grouped[project_type].sort(key=lambda x: x['last_modified'], reverse=True)
    
    # Create flat list with type headers
    flat_list = []
    for project_type in sorted(grouped.keys()):
        projects_of_type = grouped[project_type]
        # Add type header
        flat_list.append({
            'name': f"{project_type} ({len(projects_of_type)} projects)",
            'path': '',
            'relative_path': '',
            'type': project_type,
            'last_modified': 0,
            'is_header': True
        })
        # Add projects
        flat_list.extend(projects_of_type)
    
    return flat_list

def display_projects(projects, selected_index=0, group_by_type=False):
    """Display projects list with selection highlight"""
    os.system('clear')  # Clear screen
    
    mode_text = "Grouped by Type" if group_by_type else "Recent Projects"
    print(f"🔍 Project Finder - {mode_text}")
    print("=" * 50)
    print(f"Found {len([p for p in projects if not p.get('is_header', False)])} projects\n")
    
    # Show only a window of projects around the selection
    window_size = 15
    start_idx = max(0, selected_index - window_size // 2)
    end_idx = min(len(projects), start_idx + window_size)
    
    if end_idx - start_idx < window_size and start_idx > 0:
        start_idx = max(0, end_idx - window_size)
    
    for i in range(start_idx, end_idx):
        project = projects[i]
        
        if project.get('is_header', False):
            # Display type header
            print(f"🏷️  {project['name']}")
            continue
        
        prefix = "► " if i == selected_index else "  "
        type_icon = get_type_icon(project['type'])
        
        # Format date as YYYY-MM-DD
        modified_date = datetime.fromtimestamp(project['last_modified']).strftime('%Y-%m-%d')
        
        # Extract just the project path without "development/"
        path_parts = project['relative_path'].split('/')
        if path_parts[0] == 'development' and len(path_parts) > 1:
            clean_path = '/'.join(path_parts[1:])
        else:
            clean_path = project['relative_path']
        
        # Remove project name from end of path to avoid duplication
        if clean_path.endswith('/' + project['name']):
            clean_path = clean_path[:-len('/' + project['name'])]
        
        if group_by_type:
            # Indented format for grouped view
            print(f"   {prefix}• {project['name']} - {clean_path} (modified: {modified_date})")
        else:
            # Standard format for recent view
            print(f"{prefix}{type_icon} {project['name']} - {clean_path} (modified: {modified_date})")
    
    if len(projects) > window_size:
        print(f"\n... showing {start_idx + 1}-{end_idx} of {len(projects)}")
    
    print("\n" + "─" * 50)
    print("⬆️⬇️  Navigate | Enter: Open | /: Search | t: Toggle Sort | q: Quit")

def open_in_vscode(project_path, project_name):
    """Open project in VSCode and print cd command for shell wrapper"""
    try:
        subprocess.run(['code', project_path], check=True)
        print(f"✅ Opened {project_name} in VSCode")
        print(f"CD_TO:{project_path}")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ Failed to open {project_path} in VSCode")
        return False
    except FileNotFoundError:
        print("❌ VSCode command 'code' not found")
        return False

def get_char():
    """Get a single character from stdin"""
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
        # Fallback for Windows
        import msvcrt
        return msvcrt.getch().decode('utf-8')

def search_mode(all_projects, group_by_type=False):
    """Interactive search mode that respects the current view"""
    query = ""
    # Get only actual projects, not headers
    original_projects = [p for p in all_projects if not p.get('is_header', False)]
    
    while True:
        # Filter projects based on current query
        filtered_projects = fuzzy_search(
            query, 
            original_projects, 
            key_func=lambda p: f"{p['name']} {p['relative_path']}"
        )
        
        # Apply grouping if needed
        if group_by_type and filtered_projects:
            display_projects_list = group_projects_by_type(filtered_projects)
        else:
            display_projects_list = filtered_projects
        
        os.system('clear')
        search_mode_text = "Search - Grouped by Type" if group_by_type else "Search - Recent"
        print(f"🔍 {search_mode_text}")
        print("=" * 50)
        print(f"Query: {query}_")
        print(f"Found {len(filtered_projects)} matches\n")
        
        # Show top 15 results
        count = 0
        for i, project in enumerate(display_projects_list[:15]):
            if project.get('is_header', False):
                print(f"🏷️  {project['name']}")
                continue
            
            count += 1
            type_icon = get_type_icon(project['type'])
            
            # Extract clean path
            path_parts = project['relative_path'].split('/')
            if path_parts[0] == 'development' and len(path_parts) > 1:
                clean_path = '/'.join(path_parts[1:])
            else:
                clean_path = project['relative_path']
            
            if clean_path.endswith('/' + project['name']):
                clean_path = clean_path[:-len('/' + project['name'])]
            
            if group_by_type:
                print(f"   {count:2d}. • {project['name']} - {clean_path}")
            else:
                print(f"{count:2d}. {type_icon} {project['name']} - {clean_path}")
        
        print("\n" + "─" * 50)
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
        
        # Bounds checking
        if new_index < 0:
            # Find first selectable item
            new_index = next((i for i, p in enumerate(projects) if not p.get('is_header', False)), 0)
            break
        elif new_index >= len(projects):
            # Find last selectable item
            new_index = next((i for i in range(len(projects)-1, -1, -1) if not projects[i].get('is_header', False)), len(projects) - 1)
            break
        
        # Check if this is a selectable project (not a header)
        if not projects[new_index].get('is_header', False):
            break
    
    return new_index

def main():
    # Uncomment for debugging
    debug_config()
    
    print("🔍 Scanning directories:")
    projects = find_git_projects()
    
    if not projects:
        print("\n❌ No git repositories found")
        print("\nTip: Make sure you have git repositories in one of these directories:")
        for dev_dir in DEVELOPMENT_DIRS:
            print(f"  - {dev_dir}")
        print("\nOr modify the DEVELOPMENT_DIRS list in the script to match your setup.")
        return
    
    group_by_type = False
    current_projects = projects
    selected_index = 0
    
    while True:
        # Update display based on current sort mode
        if group_by_type:
            current_projects = group_projects_by_type(projects)
            # Ensure selected index is on a selectable item
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
                # Toggle sort mode
                group_by_type = not group_by_type
                continue
            elif char == '/':
                search_results = search_mode(projects, group_by_type)
                if search_results:
                    current_projects = search_results
                    # Find first selectable item in search results
                    selected_index = next((i for i, p in enumerate(current_projects) if not p.get('is_header', False)), 0)
                    # Don't change group_by_type - stay in current view mode
            elif ord(char) == 13:  # Enter
                if (current_projects and 
                    selected_index < len(current_projects) and 
                    not current_projects[selected_index].get('is_header', False)):
                    project = current_projects[selected_index]
                    if open_in_vscode(project['path'], project['name']):
                        break
            elif char == '\x1b':  # Arrow keys start with escape
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
                # Quick selection by number (find the nth selectable project)
                num = int(char)
                selectable_projects = [(i, p) for i, p in enumerate(current_projects) if not p.get('is_header', False)]
                if 1 <= num <= len(selectable_projects):
                    selected_index = selectable_projects[num - 1][0]
                    project = current_projects[selected_index]
                    if open_in_vscode(project['path'], project['name']):
                        break
                        
        except KeyboardInterrupt:
            break
        except:
            # Handle any input errors gracefully
            continue
    
    print("\n👋 Goodbye!")

if __name__ == "__main__":
    main()