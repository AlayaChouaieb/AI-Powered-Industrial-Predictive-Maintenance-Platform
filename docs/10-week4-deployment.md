# Week 4 — Integration and Deployment

## Deployment tasks
- Containerize API and database.
- Use environment variables for credentials and URLs.
- Add database health check and API health check.
- Provide demo-data seed/replay script.
- Add automated tests and a smoke test.
- Document local deployment and reset procedure.

## Smoke test
1. `docker compose up --build -d`
2. `curl http://localhost:8000/health`
3. Register `M-001`.
4. Submit a valid measurement.
5. Query machine history.
6. Confirm measurement remains after API restart.
7. Submit invalid values; expect HTTP 422.
8. Stop services and document the result.

## Security notes for a student prototype
- Do not commit production credentials.
- Replace the example PostgreSQL password before deployment.
- Keep the API/database ports private on a real VPS.
- Add authentication, TLS and rate limiting before public exposure.
