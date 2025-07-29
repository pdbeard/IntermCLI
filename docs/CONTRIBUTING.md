# Contributing to IntermCLI

We welcome contributions—new tools, features, bug fixes, and docs!

## Quick Contribution Guide
1. Fork the repo
2. Create a feature branch from `staging`: `git checkout -b feature/my-feature staging`
3. Add your tool in `tools/` with its own README and config
4. Add your tool to `tools_manifest.toml`
5. Test with both minimal and enhanced dependencies
6. Submit a PR to merge into the `staging` branch with a clear description

## Tool Guidelines
- Use `action-target` naming (e.g., `scan-ports`, `find-projects`)
- Each tool should be self-contained, with its own config and README
- Use TOML for all config files
- Follow the [Output Style Guide](/docs/output-style-guide.md) for consistent user experience
- Use the shared [utilities](/docs/shared-utilities/index.md) for configuration, output, argument parsing, etc.
- Progressive enhancement: stdlib core, optional enhancements

## Testing
- Test with stdlib only and with all optional dependencies
- Include unit and integration tests
- Test on Python 3.9+
- Use `pytest` and tools from `requirements-dev.txt`


## Code Style & Pre-commit Hooks
- Use [black](https://github.com/psf/black) for formatting
- Use [isort](https://github.com/PyCQA/isort) for import sorting
- Use [ruff](https://github.com/astral-sh/ruff) for linting
- Pre-commit hooks are configured in `.pre-commit-config.yaml` and run automatically before each commit:
    - Formatting: black, isort
    - Linting: ruff
    - Whitespace, YAML, merge conflict, shebang, docstring, and secret checks
    - To enable: run `pre-commit install` after cloning
    - To run manually: `pre-commit run --all-files`
    - To update hooks: `pre-commit autoupdate`


## PR Workflow
- All changes should be submitted via pull request to the `staging` branch
- PRs must pass CI (lint, tests, audit, pre-commit)
- Write clear commit messages and PR descriptions
- Only stable, tested changes in `staging` are promoted to `main`


## Branching & Releases
- Production-ready code is maintained in the `main` branch
- All development changes are merged into `staging` first for testing
- After validation in staging, changes are promoted to `main` via pull request
- Use feature branches for development work, branched from `staging`

---

- Type annotations are encouraged (use [mypy](http://mypy-lang.org/))
- Keep code readable and modular
## Security & Quality
- Pre-commit hooks include checks to prevent committing secrets and merge conflicts
- Use [Dependabot](https://github.com/dependabot) for automated dependency updates
- Add a `SECURITY.md` for vulnerability reporting (recommended)
## Automation & Makefile
- Consider adding a `Makefile` or `tasks.py` for common dev tasks (lint, test, format, docs)
## Additional Tips
- Run `pre-commit autoupdate` regularly to keep hooks up to date
- Use `pre-commit run --all-files` before submitting a PR to catch issues early

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

## 🌳 Branching Strategy

- **main**: Production-ready, stable code only
- **staging**: Pre-production testing environment where all changes are validated
- **feature/**: New features (e.g., `feature/scan-ports-enhancement`)
- **bugfix/**: Bug fixes (e.g., `bugfix/fix-port-scan-timeout`)
- **docs/**: Documentation updates (e.g., `docs/update-installation`)
- **hotfix/**: Urgent production fixes (e.g., `hotfix/critical-security-issue`)

### Workflow

1. Create a feature, bugfix, or docs branch from the latest `staging` branch
2. When work is complete, submit a pull request to merge into `staging`
3. After code review and testing in the staging environment, your changes will be merged
4. Once `staging` is stable and ready for release, a pull request is created to merge `staging` into `main`
5. The `main` branch always contains production-ready code

---

## 🏷️ Semantic Versioning

- `v1.0.0`    Major: Breaking changes, new tool additions
- `v1.1.0`    Minor: New features, non-breaking changes
- `v1.1.1`    Patch: Bug fixes, documentation updates

---

## 🚀 Release Process

1. Ensure all intended changes are merged into `staging`
2. Thoroughly test the `staging` branch (all supported Python versions)
3. Update `CHANGELOG.md` in the `staging` branch
4. Update version numbers in relevant files
5. Update `tools_manifest.toml` and configuration docs if needed
6. Create a pull request from `staging` to `main`
7. After approval and merge to `main`, create a GitHub release with appropriate tag
8. Continue development in `staging` for the next release cycle

---

Thank you for helping make IntermCLI better for everyone! Your contributions are greatly appreciated.
