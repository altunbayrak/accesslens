# Deployment guide

1. Provision PostgreSQL, Redis, an S3-compatible bucket, and a container platform.
2. Set `DATABASE_URL`, `REDIS_URL`, `CORS_ORIGINS`, GitHub OAuth/App credentials, and object-storage credentials from a secret manager. Do not enable `DEMO_MODE`.
3. Run `alembic upgrade head` as a release task.
4. Run API and browser workers in separate service accounts. Workers should have outbound-only networking, DNS policy enforcement, CPU/memory quotas, no host mounts, and ephemeral browser profiles.
5. Serve the dashboard/API behind TLS. Restrict database and Redis to private networks. Monitor failed URL-validation events and queue depth.

Lighthouse requires Chromium and Node in the worker image; use a dedicated worker image in production.
