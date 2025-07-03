"""
Common utilities for LLM honesty evaluation experiments.
"""
from .evaluator import HonestyEvaluator, EvaluationResult, EvaluationScores
from .config import (
    get_api_key, 
    check_api_keys, 
    setup_logging,
    DEFAULT_FIRST_MODEL,
    DEFAULT_SECOND_MODEL,
    DEFAULT_TEMPERATURE,
    DEFAULT_MAX_TOKENS
)

__all__ = [
    'HonestyEvaluator',
    'EvaluationResult', 
    'EvaluationScores',
    'get_api_key',
    'check_api_keys',
    'setup_logging',
    'DEFAULT_FIRST_MODEL',
    'DEFAULT_SECOND_MODEL', 
    'DEFAULT_TEMPERATURE',
    'DEFAULT_MAX_TOKENS'
]