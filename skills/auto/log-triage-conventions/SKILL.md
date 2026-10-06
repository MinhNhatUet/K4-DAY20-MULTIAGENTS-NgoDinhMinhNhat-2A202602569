---
name: log-triage-conventions
description: Use when you need to parse logs and generate structured error reports according to specified conventions.
---
1. Read the log file and filter entries to include only ERROR or CRITICAL levels.
2. Convert timestamps to UTC format (YYYY-MM-DDTHH:MM:SSZ).
3. Extract the service name, ensuring it is in lower-case with '-' replaced by '_'.
4. Capture the error message from the log entry.
5. Extract the exception details from the traceback, setting to `null` if absent.
6. Count occurrences of each error message to determine `repeat_count`.
7. Aggregate counts by service for the `counts_by_service` object.
8. Ensure the output JSON structure includes `schema_version` and `generated_by` fields.
9. Sort errors by service name and then by timestamp in ascending order.
10. Write the structured output to a JSON file, ensuring it adheres to the specified schema.

Completion Checks:
- All entries are filtered correctly.
- Timestamps are in the correct format.
- Service names are formatted as required.
- The output JSON structure is valid and complete.
