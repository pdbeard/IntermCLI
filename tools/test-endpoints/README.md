# test-endpoints

Command-line API testing tool for developers who want a fast, scriptable alternative to GUI tools like Postman.

## Usage

```bash
# Basic usage with GET request
test-endpoints https://api.github.com/users/octocat

# POST request with JSON body
test-endpoints POST https://httpbin.org/post --json '{"name": "test"}'

# Custom headers
test-endpoints GET https://api.example.com/data --header "Authorization: Bearer token123"

# Using collections and environments
test-endpoints --collection my-api --request "Get Users" --env dev

# Output response in different formats
test-endpoints https://api.github.com/users/octocat --format json
test-endpoints https://api.github.com/users/octocat --format yaml
test-endpoints https://api.github.com/users/octocat --format text

# Save response to a file
test-endpoints https://api.github.com/users/octocat --format json --output result.json
```

## Configuration

| Option | Default | Description |
|--------|---------|-------------|
| `--method` | `GET` | HTTP method (GET, POST, PUT, DELETE, etc.) |
| `--header` | None | Add request header (can be used multiple times) |
| `--json` | None | JSON body for the request |
| `--format` | `auto` | Output format: `auto`, `json`, `yaml`, or `text` |
| `--collection` | None | Use a saved collection from config |
| `--env` | None | Environment to use (dev, test, prod) |
| `--verbose` | `false` | Show detailed request/response info |
| `--timeout` | `30` | Request timeout in seconds |

## Advanced Usage

For more detailed documentation on collections, environments, and request scripting, see the [comprehensive documentation](../docs/tools/test-endpoints.md).

### Optional dependencies

To enable YAML output, install `pyyaml`:

```bash
pip install pyyaml
```

For colorized output, install `rich`:

```bash
pip install rich
```

## Features

- Supports all common HTTP methods (GET, POST, PUT, DELETE, PATCH, etc.)
- Request body support for JSON
- Custom headers and query parameters
- Collection and environment support via TOML configuration
- Output response in multiple formats: JSON, YAML, or plain text
- Response validation and assertions
- Optional colorized output with rich formatting
- (Planned) Export/import of collections from/to Postman
- Scriptable for CI/CD integration
