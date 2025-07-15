## test-endpoints

Command-line API testing tool for developers who want a fast, scriptable alternative to GUI tools like Postman. Test REST APIs, GraphQL endpoints, and webhooks directly from your terminal.

**Example usage:**
```bash
test-endpoints https://api.github.com/users/octocat
test-endpoints POST https://httpbin.org/post --json '{"name": "test"}'
test-endpoints GET https://api.example.com/data --header "Authorization: Bearer token123"
test-endpoints --collection my-api --request "Get Users" --env dev
```

**Features:**
- Supports GET, POST, PUT, DELETE, etc.
- JSON and form data
- Custom headers and query params
- Collection and environment support via TOML
- Optional colorized output with rich

---

For more details, see each tool's README in its respective directory.
