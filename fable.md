# Critical Analysis: intermCLI

*Generated 2026-07-09 from branch `staging` (HEAD `7befc72` + working-tree changes).*

> **Resolution pass — 2026-07-21 (branch `staging`).** Every finding below is
> annotated with its status: **✅ FIXED**, **⏭️ SKIPPED** (with reason), or
> **ℹ️ NOTE**. After the pass: `174 passed, 40 skipped`, ruff + black clean, and
> `test_install.sh` passes. Crash paths (bugs 2–6) were each verified by running
> the tool, not just the suite. See the per-item notes and the
> [Resolution summary](#resolution-summary) at the end.

## Executive summary

intermCLI is a well-intentioned suite with a genuinely good core idea: small stdlib-first CLI tools sharing a common foundation (config, output, errors, networking), with optional dependencies unlocking enhancements. The docs, config precedence design, and CI matrix show real care.

The execution, however, has a systemic problem: **the tools and the shared library have drifted apart.** Multiple tools call shared-module methods that don't exist, so several user-facing error paths and one advertised feature crash with `AttributeError`/`TypeError` instead of working. The test suite (167 passing tests) doesn't catch any of these because it heavily mocks the seams where the breakage lives — and right now the suite doesn't even collect due to a syntax error in an uncommitted test file. There is also a fair amount of dead code, duplicated fallback logic, and one truly alarming hack (call-stack introspection to find config in `sort-files`).

None of this is fatal — the issues are concentrated and fixable — but the project currently fails its own stated goal of a "robust shared foundation."

---

## What works well

- **Architecture concept.** Tools + `shared/` + TOML config with documented precedence is the right shape for this project. `path_utils.require_shared_utilities()` gives friendly failures.
- **Progressive enhancement.** The rich/requests-optional pattern is consistently attempted across tools, and `DependencyChecker` with a manifest is a nice touch.
- **CI is serious for a hobby-scale project**: 4 Python versions × 3 OSes, ruff, black, pre-commit, pip-audit, coverage upload.
- **`SecurityValidator` in find-projects** shows unusual (for this kind of tool) attention to editor-command validation, symlink escape, and scan limits — even if parts are flawed (see below).
- **install.sh** has interactive prompts, dry-run, uninstall, PATH management, and cleanup traps — more complete than most.

---

## Confirmed bugs (verified by execution, not just reading)

These were each reproduced against the current code:

1. **Test suite does not collect.** `tests/dependency_checker_test.py:24` has an unclosed parenthesis (in your uncommitted changes). `pytest` aborts collection entirely, so *zero* tests run right now. Excluding that file: 167 pass, 40 skipped.
   **✅ FIXED** — closed the paren. Suite now collects and runs (174 passed).

2. **find-projects: "no projects found" path crashes.** `_show_no_projects_message` (find-projects.py:819) calls `output.print_list(self.config.development_dirs, title=...)`, but the signature is `print_list(title, items, ...)` → `TypeError: got multiple values for argument 'title'`. A first-run user with no repos gets a traceback instead of the help message.
   **✅ FIXED** — call now passes `title=` and `items=`. Verified by running find-projects against an empty dir: prints the tip list, no traceback.

3. **find-projects: error path in project opening crashes.** `ProjectOpener.open_project` (find-projects.py:661) calls `self.error_handler.handle_error(...)` — `ErrorHandler` has no such method. Any unexpected exception while opening a project raises `AttributeError` inside the exception handler.
   **✅ FIXED** — added `ErrorHandler.handle_error(exception, context)` (delegates to `_handle_generic`).

4. **test-endpoints: invalid `--json` input crashes.** Line 767 calls `error_handler.handle_value_error(...)` — the method doesn't exist. Passing malformed JSON produces an `AttributeError` traceback instead of the intended "Invalid JSON" message.
   **✅ FIXED** — added `ErrorHandler.handle_value_error(value_desc, exception, operation)`. Verified: malformed `--json` now prints "Invalid JSON: …".

5. **test-endpoints: the collections feature is unimplemented but advertised.** The module docstring and README promote `--collection/--request/--env`; the flags are parsed (lines 691–699) but never read in `main()`. Worse, `load_collection` (line 566) constructs `ConfigLoader(TOOL_NAME, section_name="collections")` — `ConfigLoader.__init__` takes no `section_name`, so it would raise `TypeError` if it were ever called.
   **✅ FIXED (by removal)** — dropped the unimplemented `--collection/--request/--env/--set` flags, deleted `load_collection`, and updated the docstring/example. Implementing a full collections system was out of scope for a bug pass; removing the false advertisement was the actionable fix. (`substitute_variables` was kept — it's independently tested.)

6. **test-endpoints: dead "preferred" request path.** `make_request` (line 202) probes `network_utils.http_request`, but the shared method is named `make_http_request`. The `hasattr` check always fails, so the "use shared NetworkUtils first" branch is unreachable dead code and every request silently falls through to the tool's own duplicated request logic.
   **✅ FIXED (by removal)** — a rename alone would introduce a real bug: `make_http_request` returns a *dict*, but the printers and `make_request` need a response *object* (attribute access, `response.elapsed = …`). Removed the dead branch; the tool's own requests/urllib paths (which respect `verify_ssl`) now run directly. Verified: live `GET https://example.com` → 200.

7. **shared/dependency_checker.py:80–94: literal copy-paste duplication** — the same `if missing:` block appears twice, so in the non-rich path the "To enable all features, install…" line prints twice.
   **✅ FIXED** — removed the duplicate block.

8. **find-projects: tool defaults are silently discarded.** `ConfigManager.load_config` sets `self.config_loader.config = default_config` (line 224) and then calls `load_config()`, which rebuilds from `ConfigLoader._get_default_config()` and ignores the assigned dict. The tool's carefully constructed defaults only survive via the pile of `setdefault()` calls that follow — the config plumbing doesn't actually work the way the code implies.
   **✅ FIXED** — `ConfigLoader.load_config` now merges any caller-assigned `self.config` over the built-in defaults as a base layer (below file/env/cmd overrides), so tool defaults genuinely flow through.

---

## Design and architecture issues

### The shared library and its consumers have no contract
Bugs 2–6 above are all the same failure class: a tool calling an interface the shared module doesn't expose. Nothing enforces the boundary — no type-checking of cross-module calls in CI (mypy is installed in dev deps but not run in `ci.yml`), and the tests mock `Output`/`ErrorHandler`/`NetworkUtils` so mismatches never surface. Running `mypy` across `tools/` + `shared/` in CI would have caught every one of these.
**⏭️ SKIPPED (the CI/mypy change).** The individual mismatches (bugs 2–6) are all fixed. Adding `mypy` to `ci.yml` is worthwhile but a CI change beyond this bug pass, and it would surface a batch of pre-existing type issues to triage first.

### sort-files: call-stack introspection to find config
`get_destination_folder` (sort-files.py:189–206) uses `inspect.getouterframes` to **walk up the Python call stack looking for a local variable named `config`** in any caller's frame, to read size thresholds. This is the most fragile pattern in the codebase — invisible coupling, breaks under refactoring or threading, and untestable. Compounding it: `main()` bypasses the module's own `load_config()` (which computes `huge_size`/`large_size`/`medium_size`) and calls `ConfigLoader.load_config()` directly (line 410), so the frame-walk finds a config *without* those keys and always falls back to hardcoded defaults. Net effect: **a user's `[size_thresholds]` config is silently ignored** in `--by size` mode. Also, `sort-files.load_config()` implicitly returns `None` when an error occurs and `output` is None (line 93–102 has no fallback return).
**✅ FIXED (all three).** Deleted the `inspect` stack-walk; thresholds are now an explicit `size_thresholds` parameter threaded through `get_destination_folder`/`sort_files`. `main()` now uses the module's `load_config(config_path=args.config, …)` — so `--config` is honored (it was silently ignored before) and thresholds are wired into the real path. `load_config` now always returns a dict (no implicit `None`). Also fixed inverted precedence uncovered here: an explicit `--config` file now wins over the tool's baked defaults. Verified: a config lowering thresholds correctly reclassifies a 200-byte file as `huge`.

### interm: the launcher can't launch
`delegate_to_tool` (interm.py:227) is fully implemented but **never called** — `main()` only dispatches `list/version/about/status` and prints help for anything else. `interm scan-ports localhost` does nothing useful. Also, `logger` is created only under the `if __name__ == "__main__"` guard (line 259), so importing the module and calling `get_tools_from_manifest()` raises `NameError`. interm also carries its own triple-fallback TOML loader (lines 35–56) duplicating what `ConfigLoader` already solves.
**✅ FIXED (launcher + logger).** `main()` now treats an unrecognized command as a tool name and delegates via `delegate_to_tool`; `logger` is defined at module scope so importing the module is safe. Verified: `interm sort-files --help` delegates, unknown tools report an error. **⏭️ SKIPPED (triple TOML loader):** it works and is used by `get_global_config` on a path `ConfigLoader` doesn't cover; left as-is to avoid a behavior change.

### ConfigLoader: cross-tool config bleed
`_get_config_files` (config_loader.py:136–140) globs **every** `*.toml` in the project `config/` directory into every tool's config, and unconditionally loads `tools_manifest.toml` into each tool's namespace. So scan-ports' config dict quietly contains sort-files' rules and the manifest. Since these load *last*, they can also *override* the user's own settings, inverting the documented precedence. Related: `config_source` only records the last file loaded, so `--show-config` reports a misleading single source; and if a tool is run from any directory containing a `config/` folder, arbitrary TOML from that unrelated project gets ingested (`Path.cwd() / "config"`, line 123).
**✅ FIXED (glob scoping).** The project-`config/` glob is now an ordered allowlist (`dependency_manifest`, `tools_manifest`, `defaults`, then `{tool}.toml` last) instead of every `*.toml`, so a tool no longer ingests unrelated tools' configs, and tool-specific files sit highest in that tier. `tools_manifest.toml` is intentionally kept (interm depends on it). **ℹ️ NOTE:** `config_source` still records only the last file (cosmetic `--show-config` label), and the `Path.cwd() / "config"` discovery remains — both left as pre-existing minor behavior.

### Global mutable state and thread races in scan-ports
Everything hangs off module globals (`output`, `network_utils`, …) initialized in `main()`. Service detection runs `comprehensive_service_detection` in a `ThreadPoolExecutor` (scan-ports.py:669), and each helper mutates the **shared** `network_utils.timeout` (e.g. line 206, 216, 229) — a data race across worker threads. Timeouts should be per-call parameters, not instance mutation. Also inconsistent: `handle_list_scan` gates rich output on `output.rich_console` (respects `--no-color`), while `scan_all_configured_ports` gates on the module-level `HAS_RICH and console` (line 690) and ignores `--no-color`.
**✅ FIXED (race + gating).** The three service-detection helpers no longer mutate a shared instance; they use per-timeout `NetworkUtils` instances from a small cache (`_network_utils_for`), so worker threads can't stomp each other's timeout. `scan_all_configured_ports` now gates on `output.rich_console`, so `--no-color` is respected consistently. **ℹ️ NOTE:** the broader "module-global state" design (globals set in `main()`) is left as-is.

### find-projects interactive input is structurally flaky
`InputHandler.get_char()` enables raw mode, reads one char, and **restores cooked mode before returning**. Arrow-key handling (`_handle_arrow_keys`, line 1003; search mode, line 937) then reads the rest of the escape sequence via bare `sys.stdin.read(1)` in canonical mode — those reads only succeed because the bytes happen to be buffered; in canonical mode they can block until Enter. This is a classic source of "arrow keys sometimes hang" behavior. The escape sequence should be consumed inside the raw-mode window.
**⏭️ SKIPPED.** A correct fix means restructuring raw-mode input handling; it's interactive-TTY behavior that can't be verified from the test suite without real regression risk. Left for a focused change with manual terminal testing.

### Other design smells
- **find-projects `open_project`** does `os.chdir(project_path)` with no `try/finally` (line 632–642) — an exception leaves the process in the wrong cwd. `subprocess.run([editor, "."], cwd=project_path)` would remove the need entirely.
  **✅ FIXED** — switched to `subprocess.run([editor, "."], cwd=project_path)`; removed the `os.chdir` dance.
- **RateLimiter** (find-projects.py:419): when the limit trips, the loop sleeps 0.1s and `continue`s — that directory is **silently skipped**, not retried. Under load, projects go missing from results.
  **✅ FIXED** — now throttles with a short `while`-sleep and then processes the directory, so none are dropped.
- **`".git" in os.listdir(root)`** (line 435) raises `PermissionError` on unreadable dirs, and the enclosing try/except (line 442) aborts the scan of the *entire* dev directory rather than skipping the one bad dir.
  **✅ FIXED** — `os.listdir(root)` is guarded; an unreadable directory is warned and skipped, the scan continues.
- **test-endpoints `main()`** is ~230 lines mixing parser construction, config loading, banner printing, and request logic; args are added to the parser *after* the banner is printed and config loaded, so even `--help` triggers config I/O and banner output. Query params from `-p` are concatenated without URL-encoding (line 756).
  **✅ FIXED (URL-encoding):** `-p` params are now URL-encoded. **⏭️ SKIPPED (main() reordering):** the ~230-line reshuffle is a larger refactor with real regression surface; deferred.
- **Output class**: `header()` and `section()` are byte-identical duplicates; `debug()` gates on `self.verbose` but `setup_tool_output` only sets `verbose=True` when the log level string equals `DEBUG` — `output.verbose = args.verbose` is then re-set ad hoc by some tools and not others.
  **✅ FIXED (dedup):** `section()` now delegates to `header()`. **ℹ️ NOTE (verbose):** the `verbose` initialization inconsistency is left as-is (cosmetic; tools set it explicitly).

---

## Security observations

- **`NetworkUtils.make_http_request` (enhanced path) hardcodes `verify=False`** (network_utils.py:497) with no parameter to enable verification. Any future consumer of the shared HTTP helper silently gets TLS verification disabled. test-endpoints only escapes this because its "use shared utils" path is dead (bug 6) — its own fallback respects `verify_ssl`. For a *scanning* tool `CERT_NONE` is defensible; for a general-purpose shared request helper it is not. The flag should be a parameter defaulting to `True`.
  **✅ FIXED** — `make_http_request` (and the basic/enhanced helpers) now take `verify: bool = True`; the urllib path builds a `CERT_NONE` context only when `verify=False`, and the warning suppression is likewise gated.
- **`is_safe_symlink` uses string-prefix matching** (find-projects.py:126): `str(target).startswith(str(base))` means `/home/u/dev-evil` passes a check against `/home/u/dev`. The sibling method `validate_project_path` does it correctly with `Path.relative_to` — the same technique should be used here.
  **✅ FIXED** — now uses `Path.relative_to` containment, matching `validate_project_path`.
- **Env-var type coercion is too eager**: `ConfigLoader._convert_env_value` turns `"1"/"0"/"yes"/"no"` into booleans for *any* key, so `INTERMCLI_SCAN_PORTS_COMMON_TIMEOUT=1` yields `True`, not `1`.
  **✅ FIXED** — `"1"/"0"` are no longer coerced to booleans (only `true/false/yes/no`), so numeric env overrides survive as ints.
- Positives worth keeping: editor-command allowlist/regex validation, refusing to follow out-of-tree symlinks, scan depth/project-count limits, and skipping `.ssh`/`.gnupg`.
  **ℹ️ NOTE** — left intact.

---

## install.sh

- **`get_install_log_path` contains Python that can never parse** (install.sh:39,43): `python3 -c "import sys; import os; try:\n import tomllib\n ..."` — `try:` cannot follow a semicolon and `\n` inside double quotes is a literal backslash-n. Both invocations fail silently (`2>/dev/null`), so the configurable-log-dir feature is dead code that always falls back to the default.
  **✅ FIXED** — replaced with a proper `python3 - "$config" <<'PYEOF'` heredoc (`read_output_dir`) that actually parses the TOML.
- **Cleanup tracking is broken by subshells**: `INSTALLED_FILES+=(...)` happens inside `parse_tools | while read` pipelines (lines 596–613), so the array mutations occur in a subshell and are lost. `cleanup_on_failure`/`cleanup_on_exit` will never remove anything. Same subshell issue makes `verify_installation`'s `return 1` (line 121) not propagate.
  **✅ FIXED** — both loops converted to `while … done < <(parse_tools)` process substitution, so `INSTALLED_FILES` persists for cleanup and `return 1` propagates.
- **`create_tool_wrapper` (line 561) is defined and never called.** Instead the raw `.py` files are copied into `~/.local/bin` and `shared/` is copied alongside them. This works only by accident: the tool computes `parents[2]` for `sys.path` (which lands on `$HOME`, useless), and imports succeed only because Python implicitly puts the script's own directory (`~/.local/bin`) on `sys.path`, where the copied `shared/` happens to sit. Fragile, and it means installed tools run a *snapshot* of `shared/` that silently diverges from the repo. The wrapper approach (pointing back to `$SCRIPT_ROOT`) was the better design — it should be used or deleted.
  **✅ FIXED (by deletion) / ⏭️ SKIPPED (redesign).** Deleted the never-called `create_tool_wrapper` (dead code). Switching the install from copy-based to wrapper-based is a semantics change that `test_install.sh` currently locks in (it asserts an executable `.py` and a copied `shared/`), so that redesign is left as a maintainer decision.
- **Uninstall leaves `~/.local/bin/shared` behind**, and the "Note" at line 260 talks about the repo's `shared/`, not the installed copy.
  **✅ FIXED** — uninstall now removes `~/.local/bin/shared`, and the note points at the source repo instead.
- **`pip3` is a hard requirement (line 241) but is never used** — the script explicitly does not install any packages.
  **✅ FIXED** — downgraded to a soft warning; no longer aborts install.
- **Version messaging is inconsistent**: the Python-not-found error says "install Python 3.11+" (line 344), the TOML fallback says "Python 3.8+ required" (line 379), README says 3.9+, CI tests 3.9+.
  **✅ FIXED** — both messages (and the TOML-fallback minimum) now say 3.9+, matching README/CI.

---

## Testing

- 167 tests pass in 0.6s, which tells you they're mock-heavy — and indeed the mocks are exactly why bugs 2–6 survive: tests replace `Output`/`ErrorHandler`/`NetworkUtils` with `MagicMock`s that accept any method name and signature.
- **40 skips, many with reasons like "This test requires modifying the tool file"** (test_endpoints_test.py) — a direct admission that the monolithic `main()` functions are untestable as written. The skips are marking design debt, not environment constraints.
- CI runs Windows in the matrix, but the README declares Linux/macOS only, and find-projects' input handling depends on `termios` with an `msvcrt` fallback that nothing exercises. Either support Windows for real or drop it from the matrix — currently it just burns CI minutes validating mocks.
- Nothing in CI runs the tools end-to-end (`scan-ports --show-lists`, `sort-files --dry-run` on a fixture dir, etc.). A handful of subprocess smoke tests would have caught every `AttributeError`/`TypeError` above.
- `mypy` and config exist in dev requirements but are absent from `ci.yml`.

**ℹ️ NOTE (testing).** The crash paths were all verified by *running* the tools during this pass (find-projects empty-dir, test-endpoints bad `--json` + a live 200, sort-files size mode, interm delegation, scan-ports `--show-lists`). Also fixed a `set -e` counter bug in `test_install.sh` (`((PASSED++))` returned falsy at 0 and aborted the harness) so it now runs all cases. **⏭️ SKIPPED:** adding a permanent subprocess-smoke suite to CI, the mypy-in-CI step, and the Windows-matrix decision — all left as follow-ups.

## Documentation & repo hygiene

- README badge table: the **staging** row points at the `dev` branch badge, and both coverage badges point at `dev` — likely stale after a branch rename.
  **✅ FIXED** — staging row and both coverage badges repointed to `main`/`staging`.
- Loose working files at repo root and in `docs/`: `todo` (tracked), `todo.local`, `suggestions.local`, `doc-suggestions.local`, `opus4.7.md`, `git-seed-design.md`, `coverage.xml`, `docs/todo.local`, `docs/output-style-guide-new.md` next to `output-style-guide.md`. Two virtualenvs (`venv/` and `.venv/`) coexist in the working tree. Untracked is fine, but the clutter (and a tracked `todo`) suggests missing `.gitignore` entries and unfinished doc migrations.
  **✅ FIXED (partial)** — removed the empty tracked duplicate `docs/output-style-guide-new.md`. `.gitignore` already covers `coverage.xml`, `.coverage`, `*.local`, and both venvs. **ℹ️ NOTE:** the tracked `todo` was left in place (it's an active working file — a deliberate maintainer call, not clutter to delete blindly).
- Version identifiers disagree: suite `1.0.0` (interm, shared), find-projects `1.0.0`, scan-ports/test-endpoints/sort-files `0.1.0`, install.sh `v1.0.0` — no single source of truth.
  **⏭️ SKIPPED** — unifying user-facing version strings is a maintainer decision (which value, and whether to introduce a single source); not changed arbitrarily.

---

## Prioritized recommendations

1. **Fix the five API-mismatch crashes** (bugs 2–6): they're small diffs — rename/add the missing `ErrorHandler` methods or fix the call sites, fix the `print_list` call, fix `http_request` → `make_http_request`, and either implement or remove the collections flags. — **✅ DONE**
2. **Fix the broken test file** and add `mypy tools/ shared/` (or at least `pyright`) to CI — it would have prevented this entire bug class. — **✅ test file fixed / ⏭️ mypy-in-CI deferred**
3. **Delete the `inspect` stack-walk in sort-files** and pass thresholds (or the config) as a parameter; wire `size_thresholds` into the real execution path. — **✅ DONE**
4. **Make `verify=False` a parameter** in `NetworkUtils.make_http_request` defaulting to secure, and fix `is_safe_symlink` to use `Path.relative_to`. — **✅ DONE**
5. **Add 5–10 subprocess smoke tests** that run each tool's happy path and one error path for real. — **⏭️ DEFERRED (verified manually this pass; not yet codified in CI)**
6. **Decide interm's fate**: wire up `delegate_to_tool` or cut the launcher; fix the module-level `logger`. — **✅ DONE (wired up + logger fixed)**
7. **Scope ConfigLoader file discovery** to the tool's own config (`{tool}.toml`, `defaults.toml`) instead of globbing all TOML in `config/`. — **✅ DONE (allowlist)**
8. **install.sh**: adopt the (already-written) wrapper approach, fix the subshell array bug, remove the dead broken Python heredocs, align version messaging. — **✅ subshell/heredoc/version/pip3/uninstall fixed; wrapper redesign ⏭️ deferred (deleted the dead function)**
9. **Repo hygiene pass**: fix badges, gitignore local files, remove the duplicate style guide, unify version strings. — **✅ badges + duplicate guide done / ⏭️ version unification deferred**

---

## Resolution summary

*Applied 2026-07-21 on branch `staging`. `174 passed, 40 skipped`; ruff + black clean; `test_install.sh` passes.*

**Fixed (verified):** all 8 confirmed bugs; sort-files stack-walk + threshold wiring + `--config` precedence; interm launcher + logger; ConfigLoader glob scoping + tool-defaults layering + env-bool coercion; scan-ports thread-race + `--no-color` gating; `make_http_request` `verify` param; `is_safe_symlink` containment; find-projects `chdir`/rate-limiter/unreadable-dir; Output `section` dedup; test-endpoints URL-encoding; install.sh heredocs/subshells/pip3/uninstall/versions; README badges; empty duplicate doc removed; `test_install.sh` counter bug.

**Skipped (with reason):** mypy-in-CI and a permanent subprocess-smoke suite (CI changes beyond a bug pass); find-projects raw-mode input rework and test-endpoints `main()` reordering (interactive/large refactors with regression risk, unverifiable from the suite); install wrapper-vs-copy redesign (locked in by `test_install.sh`; maintainer call); version-string unification (maintainer call); interm's triple TOML loader and the `config_source`/`Path.cwd()` minor notes (left as pre-existing behavior); tracked `todo` (active working file).
