---
applyTo: "backend/**/*,*.py"
---

## Backend Guidelines

- All API endpoints must be defined in the `routers` folder.
- Load example database content from the `database.py` file.
- Log full technical error details only on the server. Return only user-friendly, non-sensitive error messages and appropriate status codes to the frontend (do not expose stack traces, queries, or other internal details).
- Ensure all APIs are explained in the documentation.
- Verify changes in the backend are reflected in the frontend (`src/static/**`). If possible breaking changes are found, mention them to the developer.