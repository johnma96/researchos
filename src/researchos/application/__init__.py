"""Application Layer — Use case orchestration.

Contains:
- agents/: Autonomous behavior (decides, iterates, calls tools)
- services/: Deterministic flows (always the same steps)

RULES:
- Depends on Domain (models, exceptions, interfaces) and Infrastructure (via Protocols)
- Orchestrates workflows but does NOT implement technical details
- Programs against Protocols from domain/interfaces.py, never against concrete infra
"""
