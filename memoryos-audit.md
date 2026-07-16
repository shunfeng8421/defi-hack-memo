# Security Audit Report — memoryos

## CVE Details

| 字段 | 值 |
|------|------|
| 项目 | suyuemian/memoryos |
| 版本 | 0.1.0 |
| CWE | CWE-306: Missing Authentication for Critical Function |
| CVSS | 8.1 (HIGH) |
| 发现日期 | July 14, 2026 |
| 发现者 | shunfeng8421 |
| Issue | [#1](https://github.com/suyuemian/memoryos/issues/1) |

## Summary

All 9 API endpoints are publicly accessible without authentication. The application is an AI agent memory engine — it stores and retrieves agent memories using OpenAI embeddings. No authentication, no API keys, no rate limiting.

## Vulnerable Endpoints

| Method | Path | Impact |
|------|------|------|
| POST | `/api/v1/agents` | Register arbitrary agents |
| GET | `/api/v1/agents` | List all registered agents |
| GET | `/api/v1/agents/{id}` | Read any agent's data |
| POST | `/api/v1/memories` | Store memories for any agent |
| POST | `/api/v1/memories/query` | Query all stored memories |
| POST | `/api/v1/memories/extract` | Extract and store new memories (uses OpenAI credits) |
| GET | `/api/v1/agents/{id}/memories` | Read all memories of any agent |
| POST | `/api/v1/agents/{id}/consolidate` | Trigger memory consolidation (uses OpenAI credits) |
| POST | `/api/v1/sessions/{id}/messages` | Append conversations to any session |

## Additional Issues

1. **CORS `allow_origins=["*"]`** — Cross-origin requests from any domain
2. **`debug=True`** — Werkzeug debugger exposes code execution in production
3. **No rate limiting** — OpenAI API credit drain possible via mass consolidation requests

## Proof of Concept

```bash
# Register an agent — no auth required
curl -X POST http://target/api/v1/agents -H "Content-Type: application/json" \
  -d '{"name":"evil-agent"}'

# Read all memories — no auth required
curl http://target/api/v1/agents/any-agent-id/memories

# Drain OpenAI credits — no auth required
for i in $(seq 1 1000); do
  curl -X POST http://target/api/v1/agents/any-id/consolidate &
done
```

## Impact

- **Data Exposure**: All agent memory data accessible to anyone
- **Data Tampering**: Inject false memories into any agent
- **Financial**: OpenAI API credit drain via consolidation loops
- **Reconnaissance**: Discover all users' agents and their memory contents

## Fix

```python
# app.py — add authentication middleware
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def verify_api_key(token: HTTPAuthorizationCredentials = Depends(security)):
    if token.credentials != os.getenv("MEMORYOS_API_KEY"):
        raise HTTPException(401)
    return token

# Apply to router
router = APIRouter(prefix="/api/v1", dependencies=[Depends(verify_api_key)])
```

## Timeline

- 2026-07-14: Discovered and reported
- 2026-07-14: GitHub Issue #1 filed
- Awaiting maintainer response
