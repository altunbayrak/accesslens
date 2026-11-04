# GitHub integration

Use GitHub OAuth for user identity and a GitHub App for repository installation, PR webhooks, check runs, and comments. Register `Checks: Read & write`, `Pull requests: Read & write`, and `Contents: Read`; keep the private key and webhook secret in a secret manager. Verify every webhook signature. The supplied workflow triggers an approved project scan; production check/comment writes should happen through a server-side GitHub App service and link only to immutable evidence.
