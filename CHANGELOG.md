# Changelog

## 1.0.0 — 2026-11-04

First production release of AccessLens.

- Authorized-domain website scan API and dashboard
- SSRF-safe target, DNS, and redirect validation
- Passive SEO and security-header analysis with remediation guidance
- Crawl/page limits, timeouts, scan history, JSON exports, and database migrations
- Isolated Playwright/axe-core browser worker and screenshot evidence channel
- Docker Compose, CI workflow, deployment guide, GitHub integration guidance, and tests

### Operational note

Lighthouse execution and GitHub OAuth/App credentials are deployment integrations: install/configure them in the dedicated worker and secret manager before enabling them in a live environment. No test target, external credential, or demo project ships enabled by default.
