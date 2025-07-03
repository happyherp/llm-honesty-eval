"""LLM Honesty Evaluation Package.

A tool for evaluating AI responses to determine if they exhibit patterns of
Truth-Seeking, Convincing, or Pandering behavior.
"""

__version__ = "0.1.0"
__author__ = "LLM Honesty Eval"
__email__ = "contact@example.com"

from .evaluator import HonestyEvaluator
from .models import EvaluationResult, HonestyScores

__all__ = ["HonestyEvaluator", "EvaluationResult", "HonestyScores"]