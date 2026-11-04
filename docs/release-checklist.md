# Production release checklist

- [x] `DEMO_MODE` defaults to false and no seed runs automatically.
- [x] No credentials are committed; `.env.example` contains placeholders only.
- [x] Build passes: `cd frontend && npm run lint && npm run build`.
- [ ] Run `cd backend && pytest` in the Docker/Python environment.
- [ ] Run `docker compose up --build` and smoke-test `/health` and `/docs`.
- [ ] Configure managed Postgres, Redis, object storage, TLS, CORS, and secret manager.
- [ ] Configure worker egress allowlists and resource limits before processing live targets.
- [ ] Configure GitHub OAuth/App secrets before enabling PR checks/comments.
