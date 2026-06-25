# Security & Privacy Architecture

The Personal Health & Medication Manager Agent incorporates strict security hardening to protect sensitive Personal Health Information (PHI).

## 1. Local-Only Storage
The application operates entirely on the local file system (`data/`). There is no external cloud syncing, preventing unauthorized remote access to health data.

## 2. Encryption at Rest (Fernet)
All health logs are encrypted using Fernet symmetric encryption. The encryption key is derived securely in memory using PBKDF2HMAC from a user-supplied 4-digit PIN. The key is never persisted to disk.

## 3. Input Sanitization
All user input is aggressively sanitized, stripping HTML and script tags before being passed to the LLM or any tools. This mitigates prompt injection and XSS vulnerabilities.

## 4. Rate Limiting
A token-bucket rate limiter restricts the agent to 20 calls per minute. This prevents denial-of-service (DoS) attacks and mitigates abuse of the LLM endpoints.

## 5. Audit Logging
Every tool execution is logged to an `audit.log` file. The log only captures metadata (timestamp and tool name) to ensure strict accountability without leaking underlying PHI.

## 6. Zero Telemetry
The application explicitly avoids sending telemetry or usage metrics to any third-party services.
