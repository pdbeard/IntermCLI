# 🐧 Linux Scripts Collection

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-linux%20%7C%20macos-lightgrey.svg)](https://github.com/yourusername/linux-scripts)

A curated collection of useful command-line utilities for development and system administration.

## ✨ Features

- 🔍 **Advanced Port Scanner** - Service detection, configurable port lists
- 📁 **Project Finder** - Interactive git repository discovery and VS Code integration
- 🔧 **Zero Dependencies** - Core functionality works with Python standard library
- 🚀 **Optional Enhancements** - Better features with optional dependencies
- 📊 **Rich Output** - Organized, colorful terminal output

## 🚀 Quick Start

```bash
# Clone and install
git clone https://github.com/yourusername/linux-scripts.git
cd linux-scripts
./install.sh

# Optional: Install enhanced features
pip3 install -r requirements.txt

# Start using
port-check --show-lists
pf
```

## 📚 Documentation

- [Port Scanner Documentation](docs/port-check.md)
- [Project Finder Documentation](docs/project-finder.md)
- [Configuration Guide](config/README.md)
- [Contributing Guidelines](docs/contributing.md)

## 🛠️ Scripts

### Port Scanner (`port-check`)
Advanced port scanner with service detection.

```bash
port-check                    # Scan all configured ports
port-check --list web         # Scan web services only
port-check -p 3000           # Check specific port
port-check --check-deps      # Show dependency status
```

### Project Finder (`pf`)
Interactive project discovery and navigation.

```bash
pf                           # Launch interactive finder
```

## 🔧 Installation

### Automatic Installation
```bash
git clone https://github.com/yourusername/linux-scripts.git
cd linux-scripts
./install.sh
```

### Manual Installation
```bash
# Copy scripts to your bin directory
cp bin/* ~/.local/bin/
chmod +x ~/.local/bin/*

# Ensure ~/.local/bin is in PATH
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
```

### Optional Dependencies
```bash
# Enhanced service detection
pip3 install requests urllib3

# Development tools
pip3 install -r requirements-dev.txt
```

## 🎯 Requirements

- **Python 3.6+**
- **Linux or macOS**
- Optional: `requests`, `urllib3` for enhanced features

## 📖 Usage Examples

<details>
<summary>Port Scanner Examples</summary>

```bash
# Basic usage
port-check localhost

# Scan specific services
port-check --list database,web

# Remote host scanning
port-check 192.168.1.100 --fast

# Custom port range
port-check -r 8000 9000
```
</details>

<details>
<summary>Project Finder Examples</summary>

```bash
# Interactive mode
pf

# Direct project search
# (Future enhancement)
```
</details>

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](docs/contributing.md) for guidelines.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a pull request

# 🖥️ IntermCLI

Interactive terminal utilities for developers

## 📚 Documentation

- **[Design Goals](docs/DESIGN.md)** - Project vision and principles
- **[Contributing](docs/CONTRIBUTING.md)** - How to contribute
- **[Architecture](docs/ARCHITECTURE.md)** - Technical details
- **[Configuration](docs/CONFIGURATION.md)** - Config file reference

## Quick Start

```bash
# Clone and install
git clone https://github.com/yourusername/intermcli.git
cd intermcli
./install.sh

# Optional: Install enhanced features
pip3 install -r requirements.txt

# Start using
interm --help
```

## ✨ Features

- 📂 **Smart Directory Navigation** - Quickly navigate to frequently used directories
- 🔍 **Enhanced Search** - Find files and content within files faster
- 🎨 **Customizable Appearance** - Themes and color schemes for better visibility
- 📊 **Usage Analytics** - Insights into your command usage patterns

## 🚀 Getting Started

1. **Installation**

   ```bash
   git clone https://github.com/yourusername/intermcli.git
   cd intermcli
   ./install.sh
   ```

2. **Basic Usage**

   ```bash
   interm navigate ~/
   interm search "TODO"
   ```

3. **Configuration**

   - Edit the config file at `~/.config/intermcli/config.yml`
   - Customize keybindings, themes, and startup commands

## 📖 Documentation

- **[User Manual](docs/manual.md)** - In-depth usage instructions
- **[Configuration Guide](docs/configuration.md)** - Config file options and examples
- **[FAQ](docs/faq.md)** - Frequently asked questions and troubleshooting

## 🤝 Contributing

We welcome contributions! Please read our [contributing guidelines](docs/CONTRIBUTING.md) before submitting a pull request.

1. Fork the repository
2. Create a new branch (`git checkout -b feature/your-feature`)
3. Make your changes
4. Commit and push (`git push origin feature/your-feature`)
5. Create a pull request