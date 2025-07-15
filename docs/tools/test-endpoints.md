# 🌐 test-endpoints

**test-endpoints** is a command-line API testing tool designed for developers who want a fast, scriptable alternative to GUI tools like Postman. Test REST APIs, GraphQL endpoints, and webhooks directly from your terminal with support for collections, environments, and detailed response analysis.

---

## 🚀 Purpose

Provide developers with a lightweight, terminal-native tool for API testing that integrates seamlessly into development workflows, CI/CD pipelines, and debugging sessions.

---

## ✨ Features

- **Multiple HTTP Methods**
  Support for GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS

- **Request Building**
  Headers, query parameters, request bodies (JSON, form-data, raw text)

- **Response Analysis**
  Status codes, headers, response time, body formatting (JSON, XML, HTML)

- **Collections & Environments**
  Save and organize requests, use variables for different environments (dev, staging, prod)

- **Authentication Support**
  Bearer tokens, basic auth, API keys, custom headers

- **Progressive Enhancement**
  Core functionality with stdlib, enhanced features with `requests` and `rich`

- **Export/Import**
  Compatible with Postman collections (basic import/export)

- **Scripting Support**
  Pre-request and post-response scripts (simple Python expressions)

---

## 📝 Example Usage

### Basic Requests

```bash
# Simple GET request
test-endpoints https://api.github.com/users/octocat

# POST with JSON body
test-endpoints POST https://httpbin.org/post --json '{"name": "test"}'

# Custom headers
test-endpoints GET https://api.example.com/data \
  --header "Authorization: Bearer token123" \
  --header "Content-Type: application/json"

# Query parameters
test-endpoints GET https://httpbin.org/get \
  --param "page=1" \
  --param "limit=10"
```

### Collections and Environments

```bash
# Save a request to a collection
test-endpoints POST https://api.example.com/users \
  --json '{"name": "{{username}}"}' \
  --save-to users-collection \
  --name "Create User"

# Run a saved request with environment variables
test-endpoints --collection users-collection \
  --request "Create User" \
  --env dev

# List available collections and requests
test-endpoints --list-collections
test-endpoints --collection users-collection --list
```

### Response Analysis

```bash
# Show detailed response information
test-endpoints GET https://httpbin.org/json --verbose

# Extract specific data from response
test-endpoints GET https://api.github.com/users/octocat \
  --extract ".name" \
  --extract ".public_repos"

# Save response to file
test-endpoints GET https://httpbin.org/json --output response.json

# Follow redirects and show timing
test-endpoints GET https://httpbin.org/redirect/3 --follow --timing
```

### Testing and Validation

```bash
# Assert response status and content
test-endpoints GET https://httpbin.org/status/200 \
  --assert-status 200 \
  --assert-contains "origin"

# Test multiple endpoints from a file
test-endpoints --batch endpoints.toml

# Integration with CI/CD
test-endpoints --collection api-tests --env production --exit-on-fail
```

---

## ⚙️ Configuration

Configuration is TOML-based with support for collections, environments, and global settings.

### Example Collection: `~/.config/intermcli/test-endpoints/my-api.toml`

```toml
[collection]
name = "My API Tests"
base_url = "{{base_url}}"

[environments.dev]
base_url = "http://localhost:3000"
api_key = "dev_key_123"

[environments.prod]
base_url = "https://api.myapp.com"
api_key = "prod_key_456"

[[requests]]
name = "Get Users"
method = "GET"
url = "/users"
headers = { "Authorization" = "Bearer {{api_key}}" }

[[requests]]
name = "Create User"
method = "POST"
url = "/users"
headers = { "Content-Type" = "application/json" }
body = '''
{
  "name": "{{username}}",
  "email": "{{email}}"
}
'''

[requests.create_user.assertions]
status = 201
contains = ["id", "created_at"]
```

### Global Config: `~/.config/intermcli/test-endpoints/config.toml`

```toml
[defaults]
timeout = 30
follow_redirects = true
verify_ssl = true
show_headers = false
format_json = true

[output]
color = true
verbose = false
save_responses = false
```

---

## 🔧 Advanced Features

### Environment Variables

```bash
# Use environment variables in requests
export API_TOKEN="your_token_here"
test-endpoints GET https://api.example.com/data \
  --header "Authorization: Bearer $API_TOKEN"

# Set variables for the session
test-endpoints --set username=john --set email=john@example.com \
  --collection users-collection --request "Create User"
```

### Pre/Post Request Scripts

```toml
[[requests]]
name = "Login and Get Token"
method = "POST"
url = "/auth/login"
pre_script = "import time; headers['X-Timestamp'] = str(int(time.time()))"
post_script = "token = response.json()['access_token']; set_var('auth_token', token)"
```

### Batch Testing

```bash
# Run all requests in a collection
test-endpoints --collection api-tests --run-all

# Run specific tests matching a pattern
test-endpoints --collection api-tests --pattern "*user*"

# Generate a test report
test-endpoints --collection api-tests --run-all --report junit.xml
```

---

## 📊 Output Formats

### Default Output
```
🌐 GET https://httpbin.org/json
✅ 200 OK (245ms)

Headers:
  Content-Type: application/json
  Content-Length: 429

Body:
{
  "slideshow": {
    "title": "Sample Slide Show"
  }
}
```

### Verbose Output
```
🌐 test-endpoints v0.1.0
Request:
  GET https://httpbin.org/json
  User-Agent: test-endpoints/0.1.0
  Accept: */*

Response:
  ✅ 200 OK
  📊 Response Time: 245ms
  📈 Size: 429 bytes
  🔗 Final URL: https://httpbin.org/json

Headers:
  Content-Type: application/json
  Content-Length: 429
  Server: gunicorn/19.9.0

Body (formatted):
{
  "slideshow": {
    "title": "Sample Slide Show",
    "author": "Yours Truly"
  }
}
```

---

## 🧪 Behavior Notes

- **SSL Verification**: Enabled by default, can be disabled with `--no-verify`
- **Timeouts**: 30 second default, configurable per request
- **Redirects**: Follows up to 10 redirects by default
- **Authentication**: Supports multiple auth methods with secure credential storage
- **Variables**: Environment and collection variables with precedence rules
- **Error Handling**: Clear error messages with suggested solutions

---

## 🔮 Future Ideas

- GraphQL query support with schema validation
- WebSocket testing capabilities
- Performance testing with load generation
- OpenAPI/Swagger spec validation
- Integration with popular API documentation tools
- Mock server generation from collections
- Collaborative collections with team sharing

---

## 🐍 Requirements


- No dependencies required for core features
- Optional: `requests` for enhanced HTTP features, `rich` for colorized output

---

## 📚 See Also

- [scan-ports](./scan-ports.md) - Network service discovery
- [check-ssl](./check-ssl.md) - SSL certificate validation
- [monitor-uptime](./monitor-uptime.md) - Service availability monitoring

---

Help us shape this tool!
Open an issue or PR with your API testing use cases and feature ideas.
