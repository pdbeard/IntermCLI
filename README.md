[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-linux%20%7C%20macos-lightgrey.svg)](https://github.com/pdbeard/intermcli)
[![Coverage Status](https://coveralls.io/repos/github/pdbeard/intermcli/badge.svg?branch=main)](https://coveralls.io/github/pdbeard/intermcli?branch=main)

<!-- CI Status -->
| Branch | CI Status | Coverage |
|--------|-----------|----------|
| **main** | [![CI main](https://github.com/pdbeard/intermcli/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/pdbeard/intermcli/actions?query=branch%3Amain) | [![Coverage Status](https://coveralls.io/repos/github/pdbeard/IntermCLI/badge.svg?branch=dev)](https://coveralls.io/github/pdbeard/IntermCLI?branch=dev) |
| **staging**  | [![CI dev](https://github.com/pdbeard/intermcli/actions/workflows/ci.yml/badge.svg?branch=dev)](https://github.com/pdbeard/intermcli/actions?query=branch%3Adev) | [![Coverage Status](https://coveralls.io/repos/github/pdbeard/IntermCLI/badge.svg?branch=dev)](https://coveralls.io/github/pdbeard/IntermCLI?branch=dev) |


# 🖥️ IntermCLI

A cohesive ecosystem of interactive CLI tools for developers and system administrators. IntermCLI combines modular design with a shared foundation to deliver powerful utilities for common tasks.

## Features
- Integrated ecosystem of CLI tools for developers and system administrators
- Cohesive user experience with consistent interface across all tools
- Robust shared foundation for configuration, output formatting, and error handling
- Progressive enhancement: core functionality works with stdlib, optional dependencies add features
- Cross-platform: Linux and macOS

## Quick Start
```bash
git clone https://github.com/pdbeard/intermcli.git
cd intermcli
./install.sh
```

## Available Tools

| Tool           | Description                        | Key Features |
| -------------- | ---------------------------------- | ------------ |
| scan-ports     | Port scanner with service detection| Service detection, range scanning, enhanced HTTP identification |
| find-projects  | Project discovery & navigation     | Git repository discovery, interactive fuzzy search, VS Code integration |
| sort-files     | File organizer by type/date/size   | Custom sorting rules, dry run mode, TOML configuration |
| test-endpoints | API endpoint testing tool          | Multiple HTTP methods, batch testing, response validation |

For detailed usage instructions, see each tool's README in the tools directory.

## Documentation

- [Design Vision](docs/DESIGN-VISION.md): Core philosophy and architectural approach
- [Developer Guide](docs/DEVELOPER-GUIDE.md): Architecture, design principles, and contribution workflow
- [Configuration](docs/CONFIGURATION.md): Config file locations and examples
- [Shared Utilities](docs/shared-utilities.md): Common utilities for all tools
- [CLI Tool Reference](docs/cli-tools.md): Comprehensive tool documentation

## Requirements

- **Python 3.9+**
- **Linux or macOS**
- Optional: Python packages in `requirements.txt` for enhanced features

## Contributing

We welcome contributions! See our [Developer Guide](docs/DEVELOPER-GUIDE.md) for:
- Tool development standards
- Testing requirements
- Pull request process

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.
