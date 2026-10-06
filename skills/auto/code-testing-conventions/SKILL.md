---
name: code-testing-conventions
description: Use when you need to ensure that code changes adhere to testing conventions and requirements.
---
1. Ensure all public functions have type annotations for parameters and return values.
2. Create a new test file in the `tests/` directory if needed, without modifying existing test files.
3. Add regression tests for each bug fixed, ensuring at least three tests are included in `tests/test_regressions.py`.
4. Ensure that the `CHANGELOG.md` is updated with a bullet point for each fix under the '## Unreleased' section, with at least three entries.
5. Validate that all test cases pass before finalizing changes.
6. Use `pytest` to run tests, ensuring no errors occur during execution.
7. Check that the output of tests matches expected results, especially for edge cases.
8. Document any changes made to functions in the corresponding test cases.
9. Review the test coverage to ensure all critical paths are tested.
10. If any tests fail, debug the issues and resolve them before proceeding.

Completion Checks:
- All public functions have type annotations.
- At least three regression tests are added.
- `CHANGELOG.md` is updated correctly.
- All tests pass without errors.
