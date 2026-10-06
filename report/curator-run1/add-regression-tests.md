---
name: add-regression-tests
description: Use when adding regression tests for bugs that have been fixed in the codebase.
---
1. Create a new test file named `test_regressions.py` in the `tests` directory.
2. For each bug that has been fixed, write a separate test function that replicates the issue.
3. Ensure that each test function has a descriptive name indicating the bug it tests.
4. Use assertions to verify that the fixed code behaves as expected.
5. Document the purpose of each test function in comments above the function definition.
6. Run the test suite to ensure that all tests pass, including the new regression tests.
7. Update the CHANGELOG.md to include a bullet point for each regression test added.
8. Commit the new test file and changes to the changelog with a clear message.
9. Push the changes to the repository.
10. Confirm that the new tests are included in the continuous integration pipeline.
