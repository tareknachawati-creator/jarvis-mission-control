# Jarvis Mission Control

## Local-First AI Infrastructure & Automation Engineering

Jarvis is a personal engineering project integrating local AI models,
Windows automation, event-driven architecture, and policy-governed operations.

## Architecture

- Windows 11 and PowerShell automation
- Ollama local AI integration
- Event-driven scheduling
- Policy-based authorization and execution controls
- Persistent state and recovery mechanisms
- Desktop dashboard interfaces
- Automated testing and validation

## Included Components

This repository contains selected components from the larger private Jarvis project.

### Policy-Governed Automation

- Typed event and action contracts
- Deterministic permission evaluation
- Approval requirements for restricted operations
- Fail-closed authorization
- Stopped and observation-only modes
- Event scheduling and deduplication

## Automated Tests

Four tests verify authorization, approval requirements,
unknown-action denial, and stopped-mode enforcement.

### Running the Tests

Requires Python 3.11 or newer.

Run from the repository root:

    python -m unittest discover -s tests -p "test_policy_showcase.py" -v

## Scope

This is a curated engineering showcase, not the complete Jarvis runtime.
Private memory, credentials, databases, and personal configuration are excluded.
The scheduler module requires additional integration dependencies.

## Author

Tarek Nachawati
