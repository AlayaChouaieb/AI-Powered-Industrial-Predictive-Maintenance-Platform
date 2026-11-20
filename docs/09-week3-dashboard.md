# Week 3 — Dashboard Plan

## Pages
1. **Overview:** machine count, latest status, recent measurements, open-alert placeholder.
2. **Machine detail:** time-series charts for temperature, torque, speed, tool wear; latest prediction once inference is integrated.
3. **Alerts:** severity, created time, state, acknowledge/resolve workflow.

## MVP frontend
Use a lightweight static HTML/JS dashboard first to reduce semester risk. It should call:
- `GET /api/machines`
- `GET /api/machines/{code}/measurements`

Show empty/loading/error states. Until inference is integrated, label health/prediction fields as unavailable rather than inventing them.

## Acceptance
- Dashboard loads from the API.
- Registered machine appears.
- At least 10 seeded/replayed measurements display as a table and chart.
- Refresh updates data.
- Mobile/desktop layout remains usable.
