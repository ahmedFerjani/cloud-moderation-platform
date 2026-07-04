# Cloud Moderation Platform

🚧 WORK IN PROGRESS 🚧

A cloud-native image moderation platform built using AWS serverless architecture.

---

## Prerequisites

The following SSM parameters must be created before running `terraform apply`:

```bash
aws ssm put-parameter \
  --name "/content-moderation/dev/google/client_id" \
  --value "<google-oauth-client-id>" \
  --type "SecureString"

aws ssm put-parameter \
  --name "/content-moderation/dev/google/client_secret" \
  --value "<google-oauth-client-secret>" \
  --type "SecureString"
```

These are read by the Cognito module at apply time via `data "aws_ssm_parameter"` and are never stored in Terraform state or source code.

> Obtain credentials from [Google Cloud Console](https://console.cloud.google.com) under **APIs & Services → Credentials → OAuth 2.0 Client IDs**.

---

## Terraform State Backend (S3)

This project stores Terraform state in S3 and uses native lockfiles for state locking.

Initialize Terraform before running plan or apply:

```bash
terraform init \
  -backend-config="bucket=<terraform-state-bucket>" \
  -backend-config="key=<env>/cloud-moderation-platform.tfstate" \
  -backend-config="region=<aws-region>"
```

**Notes:**

- The S3 bucket must already exist
- Enable bucket versioning
- Enable server-side encryption
- Keep Block Public Access enabled
- If backend settings change, run `terraform init -reconfigure`

---

## Frontend Configuration

### Runtime Config

The frontend loads configuration at runtime from `public/config/app.config.json`. This file is not committed — copy the template and fill in real values:

```bash
cp frontend/public/config/app.config.template.json \
   frontend/public/config/app.config.json
```

Then populate with Terraform outputs:

```bash
terraform output cognito_user_pool_id   # → cognito.authority (user pool ID segment)
terraform output cognito_client_id      # → cognito.clientId
terraform output api_endpoint           # → reference only — apiUrl uses proxy in dev
```

### API Proxy

In development, API calls are proxied through Angular's dev server to avoid exposing the real API Gateway URL in the browser:

Angular → /api/\* → proxy → API Gateway

The proxy target is configured in `frontend/proxy.conf.ts`. Replace the placeholder with your API Gateway URL:

```typescript
'/api': {
  target: 'https://<api-gateway-id>.execute-api.<region>.amazonaws.com',
  ...
}
```

> In production, CloudFront handles routing — the proxy is development-only.

---

## Git Hooks

Git hooks are centralized at repository root under `.husky`.

Run this once after cloning:

```bash
npm install
```

On pre-commit:
- **Staged format & lint:** Frontend (prettier, eslint), Backend (ruff, black, flake8)
- **Full-project type checks:** Frontend typecheck and Backend pyright (when relevant files are staged)

Config: `.husky/pre-commit` (hook), `package.json` (lint-staged rules), `frontend/package.json` (frontend scripts)

This installs Husky from root `package.json` and activates pre-commit checks for both frontend and backend changes.
Staged-file checks use root lint-staged configs split by domain:

- `.lintstaged.frontend.cjs`
- `.lintstaged.backend.cjs`

---

## License

MIT License
