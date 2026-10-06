---
name: enforce-type-annotations
description: Use when ensuring that all public functions in the package have type annotations on parameters and return values.
---
1. Review all public functions in the codebase (functions not starting with '_').
2. For each public function, check if all parameters have type annotations.
3. Verify that the return value of the function has a type annotation.
4. If any function is missing type annotations, add appropriate annotations based on the expected types.
5. Run the code linter to ensure no type-related warnings are present.
6. Document any changes made to type annotations in the CHANGELOG.md under '## Unreleased'.
7. Ensure that the updated code passes all existing tests.
8. Commit the changes with a message indicating the addition of type annotations.
9. Push the changes to the repository.
10. Confirm that the code review process is initiated for the changes made.
