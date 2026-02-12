# Codex: インフラベストプラクティス

> **消化元**: files.zip → codex-infra.md (SKILL v4.0 参照)
> **消化日**: 2026-02-12
> **第一原理**: 「インフラの落とし穴を環境で排除する」 = I-4 Guard/Prove/Undo の実装
> **HGK 対応**: Code Protocols Skill, /dev, /ene, Safety Invariants

---

## Docker

### 必須パターン

```dockerfile
# Multi-stage build
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.11-alpine AS runtime
# Non-root user
RUN adduser -D appuser
USER appuser
COPY --from=builder /app .
HEALTHCHECK --interval=30s CMD curl -f http://localhost:8080/health
```

### 禁止

| ❌ | ✅ |
|:--|:--|
| `FROM python:latest` | `FROM python:3.11-alpine` (pinned) |
| `USER root` | `USER appuser` |
| HEALTHCHECK なし | `HEALTHCHECK --interval=30s ...` |
| `RUN apt-get install && ...` 単一RUN | Multi-stage で分離 |

---

## Kubernetes

### 必須

```yaml
resources:
  requests: { cpu: "100m", memory: "128Mi" }
  limits: { cpu: "500m", memory: "256Mi" }
securityContext:
  runAsNonRoot: true
  readOnlyRootFilesystem: true
  allowPrivilegeEscalation: false
livenessProbe:
  httpGet: { path: /health, port: 8080 }
  initialDelaySeconds: 10
readinessProbe:
  httpGet: { path: /ready, port: 8080 }
  initialDelaySeconds: 5
```

### NetworkPolicy (Default Deny)

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
spec:
  podSelector: {}
  policyTypes: [Ingress, Egress]
```

---

## Terraform

### 必須

- Remote State: S3 + DynamoDB (or GCS + lock)
- Module 化: `modules/{name}/main.tf`
- Version Pinning: `terraform { required_version = "~> 1.5" }`
- Encryption: KMS for sensitive state
- Plan-Before-Apply: CI/CD で `terraform plan` レビュー

### 禁止

| ❌ | ✅ |
|:--|:--|
| Local state | Remote backend |
| `latest` AMI/image | Pinned version |
| Secret in `.tf` | Secret Manager / env |

---

## Security (OWASP Top 10)

| # | 脅威 | 対策 | HGK 対応 |
|:--|:-----|:-----|:---------|
| A01 | Broken Access Control | Least Privilege, Default Deny | I-1 破壊的操作承認必須 |
| A02 | Cryptographic Failures | TLS 1.3, Argon2id, Secret Manager | I-3 .env 保護 |
| A03 | Injection | Parameterized queries, sanitization | codex-lang 禁止パターン |
| A04 | Insecure Design | Threat Modeling, Secure by Default | /dia Pre-Mortem |

---

## Database

### PostgreSQL

```sql
-- Connection: SSL required
-- Migrations: Versioned (Alembic/Flyway)
-- Indexing: EXPLAIN ANALYZE before deploy
-- Backup: pg_dump + point-in-time recovery
```

### Redis

```
maxmemory-policy allkeys-lru
requirepass ${REDIS_PASSWORD}
rename-command FLUSHALL ""
```

---

*Codex Infra v1.0 — SKILL v4.0 消化 (2026-02-12)*
