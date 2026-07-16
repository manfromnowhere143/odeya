# Security Policy

## Current scope

Odeya is currently an architecture-only private repository. It contains specifications, schemas, adversarial fixtures, validators, and bounded formal models. It does not contain a deployed research engine, production service, credential broker, model gateway, or externally reachable application.

## Reporting

Do not open a public issue for a suspected vulnerability, exposed credential, sensitive research artifact, or privacy concern.

Use a private GitHub Security Advisory for the repository when that feature is enabled. Otherwise contact the repository owner through an already verified private channel and include only the minimum information needed to reproduce the issue.

Never place credentials, tokens, private datasets, unredacted personal information, exploit payloads against third parties, or unrestricted model transcripts in a report. A report is evidence to investigate, not authority to access another system.

## What to include

- the exact commit and affected path;
- the violated boundary or plausible impact;
- minimal deterministic reproduction steps;
- whether any external effect occurred or remains ambiguous;
- containment already performed, without destroying evidence; and
- a safe way to coordinate further validation.

## Response boundary

Receipt of a report does not establish severity, scientific validity, or permission to test production systems. Odeya will preserve the report, separate observation from inference, and record correction or containment evidence. No response-time guarantee or production support commitment is claimed at this architecture stage.
