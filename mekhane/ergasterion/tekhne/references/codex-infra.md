# THE_CODEX_INFRA: Infrastructure Specifications

インフラストラクチャ設計の強制適用仕様。

---

## Docker Specifications

### Mandatory Patterns

| Pattern | Implementation | Violation |
|:---|:---|:---|
| **Multi-Stage Build** | Build段階とRuntime段階を分離 | 単一ステージ = NG |
| **Base Image** | `alpine`または`distroless` | `ubuntu:latest` = NG |
| **Non-Root User** | `USER nonroot`必須 | root実行 = NG |
| **Health Check** | `HEALTHCHECK`命令必須 | healthcheckなし = NG |
| **Tag Pinning** | 明示的バージョンタグ | `:latest` = NG |
| **Secret Handling** | BuildKitシークレット使用 | ENV/ARGでシークレット = NG |

### Dockerfile Template

```dockerfile
# Build stage
FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt --target=/app/deps

# Runtime stage
FROM gcr.io/distroless/python3-debian12
WORKDIR /app
COPY --from=builder /app/deps /app/deps
COPY src/ /app/src/
ENV PYTHONPATH=/app/deps
USER nonroot
HEALTHCHECK --interval=30s --timeout=3s \
  CMD ["/app/healthcheck.py"]
ENTRYPOINT ["/usr/bin/python3", "/app/src/main.py"]
```

### Banned Patterns

```dockerfile
# ❌ FORBIDDEN
FROM ubuntu:latest              # → FROM ubuntu:24.04
RUN apt-get install curl        # → Multi-stage + distroless
ENV DB_PASSWORD=secret          # → BuildKit secrets
EXPOSE 22                       # → SSHポート禁止
```

---

## Kubernetes Specifications

### Mandatory Patterns

| Pattern | Implementation | Violation |
|:---|:---|:---|
| **Resource Limits** | `requests`と`limits`必須 | 無制限Pod = NG |
| **Liveness Probe** | プロセス死活確認 | probeなし = NG |
| **Readiness Probe** | サービス提供可否確認 | probeなし = NG |
| **Security Context** | `runAsNonRoot: true` | root実行 = NG |
| **Network Policy** | Default Deny + ホワイトリスト | 無制限通信 = NG |

### Pod Spec Template

```yaml
apiVersion: v1
kind: Pod
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 65534
    fsGroup: 65534
  containers:
  - name: app
    image: myapp:1.2.3
    resources:
      requests:
        memory: "128Mi"
        cpu: "100m"
      limits:
        memory: "256Mi"
        cpu: "500m"
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities:
        drop: ["ALL"]
    livenessProbe:
      httpGet:
        path: /healthz
        port: 8080
      initialDelaySeconds: 15
      periodSeconds: 20
    readinessProbe:
      httpGet:
        path: /ready
        port: 8080
      initialDelaySeconds: 5
      periodSeconds: 10
```

### Network Policy Template

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-specific
spec:
  podSelector:
    matchLabels:
      app: myapp
  ingress:
  - from:
    - podSelector:
        matchLabels:
          role: frontend
    ports:
    - port: 8080
```

---

## Terraform Specifications

### Mandatory Patterns

| Pattern | Implementation | Violation |
|:---|:---|:---|
| **Remote State** | S3 + DynamoDB Lock | local state = NG |
| **Modularity** | 再利用可能なmodules | ハードコード = NG |
| **Encryption** | 全ストレージにKMS暗号化 | 暗号化なし = NG |
| **Versioning** | provider/moduleバージョン固定 | バージョンなし = NG |

### Backend Configuration

```hcl
terraform {
  required_version = ">= 1.5.0"
  
  backend "s3" {
    bucket         = "terraform-state-prod"
    key            = "infrastructure/terraform.tfstate"
    region         = "ap-northeast-1"
    encrypt        = true
    dynamodb_table = "terraform-locks"
  }
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}
```

### Module Structure

```
modules/
├── vpc/
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
├── rds/
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
└── eks/
    ├── main.tf
    ├── variables.tf
    └── outputs.tf
```

---

## Security Specifications (OWASP Top 10)

### A01: Broken Access Control

| Requirement | Implementation |
|:---|:---|
| **Least Privilege** | RBACで最小権限 |
| **Default Deny** | 明示的許可のみ |
| **IDOR Protection** | 全リクエストで所有者確認 |

```python
# ✅ CORRECT
def get_document(user_id: str, doc_id: str) -> Document:
    doc = Document.get(doc_id)
    if doc.owner_id != user_id:
        raise PermissionDenied("Not your document")
    return doc
```

### A02: Cryptographic Failures

| Requirement | Implementation |
|:---|:---|
| **TLS** | TLS 1.3のみ |
| **Password Hash** | Argon2id または bcrypt (work factor > 12) |
| **Secrets** | Hashicorp Vault / AWS Secrets Manager |
| **Git** | `.env`は`.gitignore`に追加 |

### A03: Injection

| Requirement | Implementation |
|:---|:---|
| **SQL** | パラメータ化クエリ / ORM |
| **Command** | `exec()`禁止、ホワイトリスト |
| **Log** | CRLF文字をサニタイズ |

```python
# ❌ FORBIDDEN
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")

# ✅ CORRECT
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
```

### A04: Insecure Design

| Requirement | Implementation |
|:---|:---|
| **Rate Limiting** | Redis Token Bucket |
| **Circuit Breaker** | 外部依存へのCircuit Breaker |
| **Input Validation** | スキーマ検証必須 |

---

## Database Specifications

### PostgreSQL

| Pattern | Implementation | Violation |
|:---|:---|:---|
| **Transactions** | 複数書込みは`BEGIN/COMMIT` | auto-commit依存 = NG |
| **Indexing** | FK必ずインデックス | 未インデックスFK = NG |
| **Query Analysis** | `EXPLAIN ANALYZE`で検証 | 検証なしクエリ = NG |
| **Connection Pool** | PgBouncer / library pool | 直接接続 = NG |
| **Migrations** | Flyway / Alembic（バージョン管理） | 手動DDL = NG |

```sql
-- Migration example
-- V001__create_users.sql
BEGIN;

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);

COMMIT;
```

### Redis

| Pattern | Implementation | Violation |
|:---|:---|:---|
| **Persistence** | データ重要度でRDB/AOF設定 | 無設定 = NG |
| **Eviction** | `maxmemory` + `maxmemory-policy` | 無制限 = NG |
| **Key Naming** | コロン区切り `app:user:123` | フラット命名 = NG |

```
# Key naming convention
app:user:123:profile        # User profile
app:session:abc-def-ghi     # Session data
app:cache:query:hash123     # Query cache
app:rate:ip:192.168.1.1     # Rate limit counter
```

---

## Compliance Checklist

```
□ Docker: Multi-stage build
□ Docker: Non-root user
□ Docker: HEALTHCHECK defined
□ K8s: Resource limits set
□ K8s: Probes configured
□ K8s: Network policies applied
□ Terraform: Remote state
□ Terraform: All resources encrypted
□ Security: No hardcoded secrets
□ Security: Parameterized queries only
□ DB: Connection pooling enabled
□ DB: Migrations versioned
```
