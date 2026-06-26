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

## License

MIT License