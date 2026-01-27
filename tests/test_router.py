"""Tests for the router module."""

import pytest
from litmus_mcp import (
    route_intake,
    validate_intake,
    compute_spec_completeness,
    DEFAULT_WEIGHTS,
)


@pytest.fixture
def sample_intake():
    return {
        "experiment_type": "CELL_VIABILITY_IC50",
        "title": "Test compound viability",
        "hypothesis": {
            "statement": "Compound X kills cells",
            "null_hypothesis": "Compound X has no effect",
        },
        "compliance": {"bsl": "BSL1"},
        "turnaround_budget": {
            "budget_max_usd": 500,
            "desired_turnaround_days": 14,
        },
        "deliverables": {
            "minimum_package_level": "L1_BASIC_QC",
            "raw_data_formats": ["CSV"],
        },
        "cell_viability": {
            "cell_line": "HeLa",
            "assay_type": "CELLTITER_GLO",
        },
    }


@pytest.fixture
def sample_labs():
    return [
        {
            "lab_id": "lab_001",
            "name": "Test Lab",
            "status": "active",
            "capabilities": {
                "experiment_types": ["CELL_VIABILITY_IC50"],
            },
            "compliance": {"max_bsl": "BSL2"},
            "commercial_terms": {
                "pricing_bands": {
                    "CELL_VIABILITY_IC50": {"min_usd": 200, "max_usd": 500},
                },
                "turnaround_days": {
                    "CELL_VIABILITY_IC50": {"standard": 10},
                },
            },
            "quality_metrics": {"on_time_rate": 0.95},
            "availability": {"current_capacity": "high"},
            "deliverables_support": {
                "global": {
                    "raw_formats": ["CSV"],
                    "max_package_level": "L2_INTERPRETATION",
                },
            },
        }
    ]


def test_validate_intake_valid(sample_intake):
    valid, errors, warnings = validate_intake(sample_intake)
    assert valid is True
    assert len(errors) == 0


def test_validate_intake_missing_fields():
    intake = {"experiment_type": "CELL_VIABILITY_IC50"}
    valid, errors, warnings = validate_intake(intake)
    assert valid is False
    assert len(errors) > 0


def test_compute_spec_completeness(sample_intake):
    completeness = compute_spec_completeness(sample_intake)
    assert 0.0 <= completeness <= 1.0
    assert completeness > 0.5  # Should be fairly complete


def test_route_intake(sample_intake, sample_labs):
    result = route_intake(sample_intake, sample_labs)
    assert result.all_matches_count == 1
    assert len(result.top_matches) == 1
    assert result.top_matches[0].lab_id == "lab_001"
