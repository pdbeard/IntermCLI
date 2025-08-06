#!/bin/bash
# Test script for IntermCLI install.sh
# This script tests the install.sh script in a temporary directory.

set -e
set -o pipefail

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

PASSED=0
FAILED=0

# Create a temporary install directory
INSTALL_DIR=$(mktemp -d /tmp/intermcli-install-test.XXXXXX)

cleanup() {
    rm -rf "$INSTALL_DIR"
}
trap cleanup EXIT

run_test() {
    local test_name="$1"
    local command="$2"
    local check_func="$3"

    echo -e "${YELLOW}Running: $test_name${NC}"
    if eval "$command"; then
        if eval "$check_func"; then
            echo -e "${GREEN}✓ $test_name passed${NC}"
            ((PASSED++))
        else
            echo -e "${RED}✗ $test_name failed: post-check failed${NC}"
            ((FAILED++))
        fi
    else
        echo -e "${RED}✗ $test_name failed: install command failed${NC}"
        ((FAILED++))
    fi
    echo "----------------------------------------"
}

# Test 1: Basic install
run_test "Basic install" \
    "./install.sh --user --prefix $INSTALL_DIR --non-interactive > $INSTALL_DIR/install.log 2>&1" \
    "[ -d '$INSTALL_DIR/shared' ] && [ -f '$INSTALL_DIR/shared/output.py' ] && [ -x '$INSTALL_DIR/sort-files' ]"

# Test 2: Only install tools with install=true in manifest
# (Assumes at least one tool can be set to install=false for this test)
# You can add more logic here to modify the manifest and re-run install.sh if needed.

# Test 3: Shared directory always present
run_test "Shared directory present" \
    ":" \
    "[ -d '$INSTALL_DIR/shared' ] && [ -f '$INSTALL_DIR/shared/output.py' ]"

# Print summary
echo "=========================================="
echo "Install Script Test Summary"
echo "=========================================="
echo -e "Tests completed: $((PASSED + FAILED))"
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}All install tests passed!${NC}"
    exit 0
else
    echo -e "${RED}Some install tests failed!${NC}"
    echo -e "${YELLOW}Install log output:${NC}"
    cat "$INSTALL_DIR/install.log"
    exit 1
fi
