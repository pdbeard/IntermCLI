# Contributing to IntermCLI

We welcome contributions of all kinds—new tools, features, bug fixes, and documentation improvements!

---

## 🚀 Quick Start

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes following our conventions (see below)
4. Test thoroughly (core + enhanced functionality, multiple Python versions if possible)
5. Submit a pull request (PR) with a clear description

---

## 🎯 Tool Development Guidelines

- **Naming:** Use the action-target naming convention (e.g., `scan-ports`, `find-projects`)
- **Manifest:** Add your tool to `tools_manifest.toml` for automatic installation and discovery
- **Progressive Enhancement:** Implement a stdlib-only core, with optional enhancements if extra dependencies are available
- **Configuration:** Use TOML for all configuration files (no JSON)
- **Documentation:** Include a comprehensive README and configuration examples in your tool's directory

---

## 🧪 Testing

- Test with minimal dependencies (stdlib only)
- Test with all optional dependencies installed
- Include both unit and integration tests
- Test on multiple Python versions (3.8–3.11 recommended)
- Use `pytest`, `pytest-cov`, and other tools from `requirements-dev.txt`

---

## 🖋️ Code Style

- Use [black](https://github.com/psf/black) for code formatting
- Use [isort](https://github.com/PyCQA/isort) for import sorting
- Run [flake8](https://flake8.pycqa.org/) for linting
- Type annotations are encouraged (use [mypy](http://mypy-lang.org/))
- Keep code readable and modular

---

## 📚 Documentation

- Update the tool-specific README in `tools/{tool-name}/README.md`
- Add usage examples and configuration samples
- Update suite-level documentation if your change affects the overall system
- If you add a new tool, update `tools_manifest.toml` and the main README

---

## 📝 Pull Request Checklist

Before submitting a PR, please ensure:

- [ ] All tests pass (core and enhanced)
- [ ] Code is formatted with `black` and `isort`
- [ ] Linting passes (`flake8`)
- [ ] Tool is added to `tools_manifest.toml` (if new)
- [ ] Documentation is updated (README, config examples)
- [ ] Configuration uses TOML format
- [ ] You have tested on at least one supported Python version

---

## 🏷️ Labels for Issues/PRs

| Label              | Purpose                        |
|--------------------|-------------------------------|
| enhancement        | New features                   |
| bug                | Bug reports                    |
| tool:scan-ports    | Tool-specific                  |
| tool:find-projects | Tool-specific                  |
| documentation      | Docs only                      |
| good-first-issue   | For new contributors           |
| help-wanted        | Community help needed          |

---

## 🌳 Branching Model

- **main**: Production-ready code
- **develop**: Integration branch for features
- **feature/**: New features (e.g., `feature/scan-ports-enhancement`)
- **tool/**: Major tool-specific changes (e.g., `tool/find-projects`)
- **release/**: Release preparation (e.g., `release/v1.0.0`)

---

## 🏷️ Semantic Versioning

- `v1.0.0`    Major: Breaking changes, new tool additions
- `v1.1.0`    Minor: New features, non-breaking changes
- `v1.1.1`    Patch: Bug fixes, documentation updates

---

## 🚀 Release Process

1. Create release branch: `git checkout -b release/vX.Y.Z`
2. Update `CHANGELOG.md`
3. Update version numbers in relevant files
4. Update `tools_manifest.toml` and configuration docs if needed
5. Test thoroughly (all supported Python versions)
6. Merge to `main`
7. Create GitHub release with binaries (if applicable)
8. Merge back to `develop`

---

Thank you for helping make IntermCLI better for everyone! Your contributions are greatly appreciated.
