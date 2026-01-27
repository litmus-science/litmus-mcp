"""Litmus MCP Server - Model Context Protocol server for experiment intake and routing."""

from .router import (
    route_intake,
    validate_intake,
    compute_spec_completeness,
    RoutingWeights,
    RoutingResult,
    LabMatch,
    DEFAULT_WEIGHTS,
)

__version__ = "0.1.0"
__all__ = [
    "route_intake",
    "validate_intake",
    "compute_spec_completeness",
    "RoutingWeights",
    "RoutingResult",
    "LabMatch",
    "DEFAULT_WEIGHTS",
]
