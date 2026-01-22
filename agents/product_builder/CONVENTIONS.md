# Product Builder Agent — Conventions & Epistemic Guarantees

This document defines the **forbidden behaviors** and **epistemic invariants** that the Product Builder Agent must uphold to maintain trustworthiness.

## 1. Forbidden Behaviors

The following actions are **strictly prohibited** in production builds:

| Behavior | Reason | Enforcement |
|---|---|---|
| **Simulated/Dummy PDFs** | Violates customer trust; delivers no value | `PublisherAgent` asserts file size > 1KB before manifest creation |
| **Hallucinated File Paths** | Breaks deployment; causes 404 errors | All `digital_file_url` paths are verified to exist on disk |
| **Fake Manifest Data** | Corrupts database; misrepresents product | Manifest must include `integrity.sha256` matching actual artifact |
| **Unattributed Rubric Scores** | Makes QA unreproducible | Every rubric score must reference a `chapter_id` |
| **Silent Failures** | Hides production issues | All exceptions must be logged with context; no bare `pass` in error handlers |

## 2. Epistemic Invariants

These are **provable assertions** that must hold for any artifact leaving the system:

### 2.1 PDF Artifact Integrity
- Every PDF must be **byte-addressable on disk** (file exists, size > 0).
- The PDF's SHA-256 hash must be computed and stored in the manifest.
- The hash can be independently verified by any consumer.

### 2.2 Manifest Integrity
- Every manifest must contain an `integrity` block:
  ```json
  {
    "integrity": {
      "sha256": "<64-char hex>",
      "build_id": "<uuid>",
      "agent_version": "1.0.0",
      "generated_at": "<ISO timestamp>"
    }
  }
  ```
- The `sha256` value must match the hash of the referenced `digital_file_url` artifact.

### 2.3 Rubric Traceability
- Every rubric assessment must log:
  - `chapter_id` being evaluated
  - `category` (Story/Teaching/Conversion)
  - `score` (1-10)
  - `verdict` (PASS/FAIL)
- Scores without a `chapter_id` reference are invalid.

## 3. Enforcement Locations

| Invariant | Enforced In | Method |
|---|---|---|
| PDF > 0 bytes | `PublisherAgent.deploy()` | `assert dest_pdf.stat().st_size > 1024` |
| SHA-256 in manifest | `PublisherAgent.deploy()` | `hashlib.sha256()` |
| Chapter ID in rubric | `RubricGuard.evaluate()` | Structured logging |
| No silent failures | All agents | `logger.error()` with context |

## 4. Verification

Run `python3 test_product_builder.py` to verify:
1. Generated PDF exists and is > 1KB.
2. Manifest contains `integrity.sha256`.
3. SHA-256 of PDF matches manifest value.
