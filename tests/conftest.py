"""Pytest fixtures for pepkio-oligo-qc-instant tests."""

from __future__ import annotations

import pytest


@pytest.fixture
def mock_manifest() -> dict:
    return {
        "schema_version": "1.0",
        "tool_id": "oligo-qc-instant",
        "title": "Oligo QC Instant",
        "description": "Batch primer quality checker with GC%, multi-method Tm, hairpin and dimer flags",
        "examples": [
            {
                "name": "batch_two_primers",
                "input": {
                    "mode": "batch",
                    "polymerase_id": "q5",
                    "batch_text": "ATGCGTACGTACGTACGTACG\nGAAGGTGAAGGTCGGAGTCAAC\n",
                },
                "output": {
                    "batch": [{"overall_status": "pass"}],
                },
            },
            {
                "name": "pair_q5",
                "input": {
                    "mode": "pair",
                    "name": "GAPDH",
                    "fwd_seq": "GAAGGTGAAGGTCGGAGTC",
                    "rev_seq": "GAAGATGGTGATGGGATTTC",
                    "polymerase_id": "q5",
                },
                "output": {
                    "pair": {"overall_status": "pass"},
                },
            },
        ],
    }


@pytest.fixture
def mock_run_response() -> dict:
    return {
        "run_id": "run_instant123",
        "status": "completed",
        "result": {
            "mode": "pair",
            "polymerase_id": "q5",
            "pair": {
                "name": "GAPDH",
                "overall_status": "pass",
                "tm_fwd": 60.5,
                "tm_rev": 59.8,
            },
            "warnings": [],
        },
        "error": None,
        "result_url": "https://tools.pepkio.com/api/tools/v1/runs/run_instant123",
        "permalink": "https://tools.pepkio.com/r/run_instant123",
    }
