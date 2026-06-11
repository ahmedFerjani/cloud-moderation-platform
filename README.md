# Cloud Moderation Platform

🚧 WORK IN PROGRESS 🚧

A cloud-native image moderation platform built using AWS serverless architecture.

---

## Terraform state backend (S3)

This project stores Terraform state in S3 and uses native lockfiles for state locking.

Initialize Terraform before running plan or apply:

```bash
terraform init \
  -backend-config="bucket=<terraform-state-bucket>" \
  -backend-config="key=<env>/cloud-moderation-platform.tfstate" \
  -backend-config="region=<aws-region>"
```

Notes:

- The S3 bucket must already exist.
- Enable bucket versioning.
- Enable server-side encryption.
- Keep Block Public Access enabled.
- If backend settings change, run `terraform init -reconfigure`.

---

## License

MIT License
