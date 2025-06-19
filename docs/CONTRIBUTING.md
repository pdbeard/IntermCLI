# Contributing to IntermCLI

## 🚀 Quick Start
1. Fork the repository
2. Create feature branch: `git checkout -b feature/my-feature`
3. Make changes following our conventions
4. Test thoroughly (core + enhanced functionality)
5. Submit pull request

## 🎯 Tool Development
- Follow action-target naming convention
- Implement progressive enhancement
- Include comprehensive README
- Add configuration examples

## 🧪 Testing
- Test with minimal dependencies (stdlib only)
- Test with full dependencies
- Include both unit and integration tests

## 📚 Documentation
- Update tool-specific README
- Add usage examples
- Update suite documentation if needed

# Labels for issues/PRs
enhancement    # New features
bug           # Bug reports  
tool:scan-ports      # Tool-specific
tool:find-projects   # Tool-specific
documentation # Docs only
good-first-issue     # For new contributors
help-wanted   # Community help needed

# Main branches
main           # Production-ready code
develop        # Integration branch for features

# Example: Feature branches example
feature/scan-ports-enhancement
feature/find-projects-fuzzy-search
feature/new-tool-check-services

# Example: Tool-specific branches (for major changes)
tool/scan-ports
tool/find-projects

# Example: Release branches
release/v1.0.0
release/v1.1.0

# Semantic versioning
v1.0.0    # Major: Breaking changes, new tool additions
v1.1.0    # Minor: New features, non-breaking changes  
v1.1.1    # Patch: Bug fixes, documentation updates

# Release process
1. Create release branch: git checkout -b release/v1.1.0
2. Update CHANGELOG.md
3. Update version numbers
4. Test thoroughly
5. Merge to main
6. Create GitHub release with binaries
7. Merge back to develop
