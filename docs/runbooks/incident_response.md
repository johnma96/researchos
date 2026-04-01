# Incident Response Runbook — ResearchOS

> **Owner:** <!-- team / on-call alias -->
> **Last reviewed:** <!-- YYYY-MM-DD -->
> **Severity levels:** S1 (service down) · S2 (degraded) · S3 (minor) · S4 (cosmetic)

---

## 1. Triage — First 5 minutes

| Step | Action |
|------|--------|
| 1 | **Acknowledge** the alert in the on-call channel. |
| 2 | Open the monitoring dashboard (`/monitoring/tracer.py` traces or your APM). |
| 3 | Classify severity (S1–S4) based on user impact. |
| 4 | If S1/S2 → start a dedicated incident channel and page the lead. |
| 5 | Post an initial status update to stakeholders. |

---

## 2. LLM Provider Outage (S1)

**Symptoms:** API calls to Claude return `5xx`, timeouts spike, agent responses stop arriving.

### Diagnosis

```bash
# Review recent error logs
make logs | grep -i "LLMProvider\|anthropic" | tail -50
```

### Mitigation

1. **Activate fallback provider** (if configured):
   - Update `configs/<env>.yaml` → `llm.model` to the backup model.
   - Redeploy or restart the service:
     ```bash
     docker compose restart api
     ```
2. **If no fallback is available:**
   - Enable **graceful degradation mode**: return a cached / templated response
     explaining temporary unavailability.
3. **Communicate** estimated recovery time to stakeholders.

### Recovery

- Monitor Anthropic status page until resolved.
- Verify with a smoke test:
  ```bash
  curl -X POST http://localhost:8000/agent/ask \
    -H "Content-Type: application/json" \
    -d '{"question": "ping"}'
  ```

---

## 3. Prompt Degradation / Hallucinations (S2)

**Symptoms:** Agent accuracy drops sharply, users report incorrect or invented
information, evaluation scores fall below threshold.

### Diagnosis

```bash
# Run the evaluation suite against the current model + prompts
python scripts/evaluate_agent.py --config configs/production.yaml
```

### Mitigation

1. **Rollback prompts** if a recent prompt change is the suspected cause:
   ```bash
   git log --oneline -- src/researchos/domain/prompts/
   git checkout <last-good-sha> -- src/researchos/domain/prompts/
   ```
2. Redeploy and re-run evaluations to confirm improvement.

### Recovery

- Update the prompt test suite (`tests/unit/domain/test_prompts.py`) with the
  failing case so it doesn't recur.

---

## 4. Cost Spike / Runaway Agent (S1)

**Symptoms:** Billing alerts fire, token usage jumps 10×+, a single agent
invocation generates an unusually long chain of LLM calls.

### Mitigation

1. **Kill the runaway process immediately:**
   ```bash
   docker compose stop api
   ```
2. **Set hard limits** in `.env`:
   - `LLM_MAX_TOKENS_PER_REQUEST`
   - Loop guard in `application/agents/agent_utils.py`

---

## 5. Memory / Vector Store Corruption (S2)

**Symptoms:** Agent returns stale or contradictory context, retrieval scores
drop, Chroma returns empty results.

### Mitigation

1. **Re-ingest documents** from the source of truth:
   ```bash
   python scripts/ingest_documents.py --config configs/production.yaml --force
   ```

---

## 6. Post-Incident — After Every S1/S2

| Step | Owner | Deadline |
|------|-------|----------|
| Write a blameless post-mortem | Incident lead | +48 hours |
| Identify action items with owners | Team | +48 hours |
| Update this runbook if a new scenario was discovered | On-call | +1 week |
| Add missing monitoring / alerts | Infra | +1 sprint |

---

## Quick Reference — Key Commands

```bash
# Health check
curl http://localhost:8000/health

# Restart service
docker compose restart api

# View logs (real-time)
docker compose logs -f api

# Run evaluation suite
python scripts/evaluate_agent.py --config configs/production.yaml

# Re-ingest documents
python scripts/ingest_documents.py --config configs/production.yaml --force
```

> **Remember:** Update this runbook every time you handle an incident.
