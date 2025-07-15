# 🎯 IntermCLI Design Goals Document


# IntermCLI Design Philosophy

## Naming & Structure
- All tools use the `action-target` (verb-noun) naming convention (e.g., `scan-ports`, `find-projects`, `sort-files`)
- Each tool is self-contained, with its own config and README
- All tools are listed in `tools_manifest.toml` for modular install and management

## Core Principles
- **Interactive First:** Tools provide prompts, confirmations, and clear feedback
- **Terminal Native:** Fast startup, works with pipes/redirects, respects CLI conventions
- **Progressive Enhancement:** Core features use stdlib; optional dependencies add enhancements
- **Tool Independence:** Minimal shared code; only abstract when proven useful
- **Simple Evolution:** Start simple, refactor only when duplication is a burden

## Design Goals
- Consistent naming and structure for discoverability
- Clear, concise documentation for each tool
- Easy contribution: add new tools in `tools/` with their own README/config
- Modular install and future plugin support

---
- **Examples**: `scan-ports`, `find-projects`, `sort-files`, `check-services`
- **Benefits**: Self-documenting, tab-completable, professional
- **Avoids**: Mixed patterns, unclear command purposes

### 2. Zero Friction Installation
- Single command installation (`./install.sh`)
- No complex dependencies required
- Cross-platform compatibility (Linux, macOS)
- Individual tool symlinks in PATH
- New tools should be added to `tools_manifest.toml` for automatic installation.

### 3. Progressive Enhancement Architecture
- **Core Layer**: Python stdlib only - always works
- **Enhanced Layer**: Optional deps unlock advanced features
- **Detection**: Tools auto-detect available dependencies
- **Fallbacks**: Graceful degradation with helpful messages
- **Installer**: Prompts user to install optional dependencies for enhanced features

### 4. Tool Independence Over Shared Libraries
- Each tool in its own directory with own executable
- Shared utilities only when duplication becomes painful
- Prefer copying small functions over complex abstractions
- Easy to understand, debug, and maintain

### 5. Optional Unified Interface
- **Primary Usage**: Individual tools (`scan-ports`, `find-projects`, `sort-files`)
- **Secondary Usage**: Optional `interm` command for suite-wide functionality
- **Global Functions**: Installation management, configuration, tool discovery
- **Delegation**: `interm scan-ports` delegates to standalone tool
- **Independence Maintained**: Tools work identically whether called directly or via `interm`

### Suite Integration
- `interm` command provides value beyond individual tools
- Tool delegation is transparent and adds no overhead
- Suite-wide functions (config, status) work reliably
- Discovery features help users find appropriate tools

## 🛠️ Technical Requirements

### Core Standards
 - Python 3.9+ compatibility
- Cross-platform (Linux, macOS, WSL)
- No external binary dependencies
- UTF-8 output with emoji support

### Tool Structure
```
tools/action-target/
├── action-target.py    # Self-contained executable
├── config/             # Tool-specific configuration (TOML recommended)
├── README.md           # Tool-specific documentation
└── tests/              # Tool-specific tests (optional)
```
- **Global tool manifest**: `tools_manifest.toml` (TOML format) for modular installation and management.

### Optional Enhancements
- Rich text formatting with `rich`
- Enhanced HTTP with `requests`
- Better CLI parsing with `click`
- Advanced terminal features when available

### Performance Targets
- Sub-100ms startup time for core commands
- Responsive interactive elements
- Efficient resource usage
- Graceful handling of large datasets

## 🎨 User Experience Guidelines

### Command Discovery
- Action-target names make tools discoverable
- Tab completion reveals related tools
- Consistent `--help` output across all tools
- Clear usage examples in help text

### Output Design
- Clear visual hierarchy with optional `rich` enhancement
- Consistent emoji and color usage across tools
- Scannable information layout
- Helpful error messages with suggested solutions

### Interactive Patterns
- Intuitive keyboard navigation
- Clear action indicators
- Immediate feedback
- Graceful error recovery

### Error Handling
- Graceful degradation when dependencies missing
- Clear messages about available vs. enhanced features
- Suggested commands for installing enhancements
- Recovery options when operations fail

## 📋 Current Tools Status

### ✅ Implemented
- **scan-ports**: Network port scanning with service detection
- **find-projects**: Development project discovery with VS Code integration
- **sort-files**: Directory organization by type, date, size, or custom rules

### 🔄 Planned (Following Action-Target Pattern)
- **check-services**: Enhanced service detection and analysis
- **list-processes**: Process monitoring and management
- **monitor-network**: Network traffic monitoring
- **manage-configs**: Configuration file management

### Future Tool Categories
- **File Management**: `find-files`, `clean-projects`, `backup-configs`
- **Network Tools**: `test-connections`, `monitor-bandwidth`
- **Development**: `check-dependencies`, `analyze-logs`

## 🔧 Architecture Principles

### Independence Over Coupling
- Tools should work without each other
- Avoid complex plugin systems initially
- Prefer simple, understandable code
- Refactor only when patterns prove themselves

### Shared Infrastructure (Minimal)
- Only create shared utilities when multiple tools need identical code
- Examples: config loading patterns, dependency detection helpers
- Avoid: Shared CLI frameworks, complex abstractions

### Configuration Philosophy
- Tool-specific configs in tool directories (TOML recommended)
- Global tool manifest in TOML (`tools_manifest.toml`)
- Global configs only for suite-wide settings
- Environment variable overrides where sensible

## 🚀 Development Workflow

### Adding New Tools
1. Create `tools/action-target/` directory
2. Implement self-contained `action-target.py`
3. Add tool-specific configuration and docs
4. Add your tool to `tools_manifest.toml` for automatic installation.
5. Test both core and enhanced functionality

### Testing Strategy
- Each tool tests its core functionality independently
- Test both stdlib-only and enhanced modes
- Integration tests for installation and PATH setup
- Manual testing on target platforms

### Refactoring Guidelines
- Extract shared code only when duplication is painful
- Prefer small utility functions over large frameworks
- Keep tool independence as primary goal
- Document any shared dependencies clearly

### Release Process
- Semantic versioning for the suite
- Individual tool versioning when needed
- Automated testing on push
- Clear changelog maintenance

## 📊 Success Metrics

### User Experience
- New users can install and use any tool within 5 minutes
- Tool names clearly indicate their purpose
- Error messages lead to successful resolution
- Enhanced features provide obvious value

### Technical Quality
- All tools work with Python stdlib only
- Shared code is minimal and well-justified
- New tools follow established patterns
- Code remains readable and debuggable

## 🎯 Design Mantras

- **"Action-target naming for clarity"**
- **"Interactive by default, scriptable by design"**
- **"Work everywhere, enhanced somewhere"**
- **"Independent tools, shared vision"**
- **"Start simple, evolve naturally"**
- **"Monolithic when it makes sense"**
- **"Fast to start, powerful to use"**
- **"Helpful errors, obvious solutions"**
