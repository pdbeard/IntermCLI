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
```

## Configuration

| Option | Default | Description |
|--------|---------|-------------|
| `--method` | `GET` | HTTP method (GET, POST, PUT, DELETE, etc.) |
| `--header` | None | Add request header (can be used multiple times) |
| `--json` | None | JSON body for the request |
| `--form` | None | Form data for the request |
| `--collection` | None | Use a saved collection from config |
| `--env` | None | Environment to use (dev, test, prod) |
| `--verbose` | `false` | Show detailed request/response info |
| `--timeout` | `30` | Request timeout in seconds |

## Advanced Usage

For more detailed documentation on collections, environments, and request scripting, see the [comprehensive documentation](../docs/tools/test-endpoints.md).

## Features

- Supports all common HTTP methods (GET, POST, PUT, DELETE, PATCH, etc.)
- Request body support for JSON and form data
- Custom headers and query parameters
- Collection and environment support via TOML configuration
- Response validation and assertions
- Optional colorized output with rich formatting
- Export/import of collections from/to Postman
- Scriptable for CI/CD integration
