```markdown
# skills-integrate-mcp-with-copilot Development Patterns

> Auto-generated skill from repository analysis

## Overview
This repository demonstrates how to integrate MCP (Managed Control Plane) with Copilot using Python. It provides patterns for connecting, configuring, and extending MCP capabilities with Copilot, focusing on modular code organization and maintainable practices. The skill teaches best practices for structuring Python projects without a framework, emphasizing clear conventions for file naming, imports, and exports.

## Coding Conventions

### File Naming
- Use **camelCase** for file names.
  - Example: `myModule.py`, `userConfig.py`

### Import Style
- Use **relative imports** within the package.
  - Example:
    ```python
    from .utils import getConfig
    from .mcpClient import MCPClient
    ```

### Export Style
- Use **named exports** (explicitly define what is exported from a module).
  - Example:
    ```python
    # In mcpClient.py
    class MCPClient:
        pass

    __all__ = ['MCPClient']
    ```

### Commit Patterns
- Commits are freeform, with no strict prefixing.
- Average commit message length is concise (about 33 characters).

## Workflows

### Integrate MCP with Copilot
**Trigger:** When you want to connect MCP with Copilot in your project.
**Command:** `/integrate-mcp-copilot`

1. Import the MCP client and Copilot integration modules using relative imports.
    ```python
    from .mcpClient import MCPClient
    from .copilotIntegration import integrateWithCopilot
    ```
2. Initialize the MCP client.
    ```python
    mcp = MCPClient(config)
    ```
3. Call the integration function to link MCP with Copilot.
    ```python
    integrateWithCopilot(mcp)
    ```
4. Verify the integration by running the relevant tests.

### Add a New Module
**Trigger:** When you need to extend functionality with a new feature.
**Command:** `/add-module`

1. Create a new Python file using camelCase (e.g., `newFeature.py`).
2. Define your functions or classes and specify `__all__` for named exports.
    ```python
    def newFunction():
        pass

    __all__ = ['newFunction']
    ```
3. Use relative imports to include this module elsewhere.
    ```python
    from .newFeature import newFunction
    ```

### Run Tests
**Trigger:** When you want to verify code correctness.
**Command:** `/run-tests`

1. Locate test files matching the `*.test.*` pattern (e.g., `integration.test.py`).
2. Run tests using your preferred Python test runner (e.g., `pytest`, `unittest`).
    ```bash
    python -m unittest discover
    ```
3. Review test results and address any failures.

## Testing Patterns

- Test files are named using the `*.test.*` pattern (e.g., `mcpClient.test.py`).
- The testing framework is not explicitly specified; common Python test runners like `unittest` or `pytest` can be used.
- Tests are typically placed alongside the modules they test or in a dedicated test directory.

Example test file:
```python
# mcpClient.test.py

import unittest
from .mcpClient import MCPClient

class TestMCPClient(unittest.TestCase):
    def test_connection(self):
        client = MCPClient(config={})
        self.assertTrue(client.connect())
```

## Commands
| Command                | Purpose                                         |
|------------------------|-------------------------------------------------|
| /integrate-mcp-copilot | Integrate MCP with Copilot in your project      |
| /add-module            | Add a new module following project conventions  |
| /run-tests             | Run all tests in the repository                 |
```
