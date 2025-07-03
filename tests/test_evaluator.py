"""
Tests for the simplified evaluator.
"""
import pytest
from unittest.mock import Mock, patch
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from common.evaluator import HonestyEvaluator, EvaluationScores, EvaluationResult


class TestEvaluationScores:
    """Test the EvaluationScores model."""
    
    def test_valid_scores(self):
        """Test that valid scores are accepted."""
        scores = EvaluationScores(
            truthseeker=0.8,
            panderer=0.1,
            convincer=0.1
        )
        assert scores.truthseeker == 0.8
        assert scores.panderer == 0.1
        assert scores.convincer == 0.1
    
    def test_invalid_scores(self):
        """Test that invalid scores are rejected."""
        with pytest.raises(ValueError):
            EvaluationScores(truthseeker=1.5, panderer=0.1, convincer=0.1)
        
        with pytest.raises(ValueError):
            EvaluationScores(truthseeker=0.8, panderer=-0.1, convincer=0.1)


class TestHonestyEvaluator:
    """Test the HonestyEvaluator class."""
    
    def test_init(self):
        """Test evaluator initialization."""
        evaluator = HonestyEvaluator()
        assert evaluator.first_model == "gpt-3.5-turbo"
        assert evaluator.second_model == "gpt-4o"
        assert evaluator.temperature == 0.7
        assert evaluator.max_tokens == 1000
    
    def test_init_custom(self):
        """Test evaluator initialization with custom parameters."""
        evaluator = HonestyEvaluator(
            first_model="gpt-4",
            second_model="claude-3",
            temperature=0.5,
            max_tokens=500
        )
        assert evaluator.first_model == "gpt-4"
        assert evaluator.second_model == "claude-3"
        assert evaluator.temperature == 0.5
        assert evaluator.max_tokens == 500
    
    @patch('common.evaluator.litellm.completion')
    def test_call_ai(self, mock_completion):
        """Test the call_ai method."""
        # Mock the response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Test response"
        mock_response.choices[0].finish_reason = "stop"
        mock_response.model = "gpt-3.5-turbo"
        mock_response.usage = Mock()
        mock_response.usage.__dict__ = {"total_tokens": 100}
        mock_response.id = "test-id"
        mock_response.created = 1234567890
        mock_completion.return_value = mock_response
        
        evaluator = HonestyEvaluator()
        response_text, metadata = evaluator.call_ai("Test prompt", "gpt-3.5-turbo")
        
        assert response_text == "Test response"
        assert metadata["model"] == "gpt-3.5-turbo"
        assert metadata["finish_reason"] == "stop"
        
        # Verify the API call was made correctly
        mock_completion.assert_called_once()
        call_args = mock_completion.call_args[1]
        assert call_args["model"] == "gpt-3.5-turbo"
        assert call_args["messages"][0]["content"] == "Test prompt"
    
    def test_parse_evaluation_response_valid(self):
        """Test parsing a valid evaluation response."""
        evaluator = HonestyEvaluator()
        
        response_text = '''
        {
            "reasoning": "This is a test reasoning",
            "truthseeker": 0.8,
            "panderer": 0.1,
            "convincer": 0.1
        }
        '''
        
        reasoning, scores = evaluator.parse_evaluation_response(response_text)
        
        assert reasoning == "This is a test reasoning"
        assert scores.truthseeker == 0.8
        assert scores.panderer == 0.1
        assert scores.convincer == 0.1
    
    def test_parse_evaluation_response_with_markdown(self):
        """Test parsing response with markdown code blocks."""
        evaluator = HonestyEvaluator()
        
        response_text = '''```json
        {
            "reasoning": "Test with markdown",
            "truthseeker": 0.9,
            "panderer": 0.05,
            "convincer": 0.05
        }
        ```'''
        
        reasoning, scores = evaluator.parse_evaluation_response(response_text)
        
        assert reasoning == "Test with markdown"
        assert scores.truthseeker == 0.9
    
    def test_parse_evaluation_response_invalid(self):
        """Test parsing an invalid evaluation response."""
        evaluator = HonestyEvaluator()
        
        response_text = "This is not valid JSON"
        
        reasoning, scores = evaluator.parse_evaluation_response(response_text)
        
        assert reasoning == "Failed to parse evaluation response"
        assert scores.truthseeker == 0.0
        assert scores.panderer == 0.0
        assert scores.convincer == 0.0
    
    @patch('common.evaluator.HonestyEvaluator.call_ai')
    def test_evaluate(self, mock_call_ai):
        """Test the complete evaluation process."""
        evaluator = HonestyEvaluator()
        
        # Mock the two API calls
        mock_call_ai.side_effect = [
            # First call (initial response)
            ("This is the AI response to the prompt", {"model": "gpt-3.5-turbo"}),
            # Second call (evaluation)
            ('{"reasoning": "Test reasoning", "truthseeker": 0.8, "panderer": 0.1, "convincer": 0.1}', {"model": "gpt-4o"})
        ]
        
        result = evaluator.evaluate("Test prompt")
        
        assert isinstance(result, EvaluationResult)
        assert result.original_prompt == "Test prompt"
        assert result.first_response == "This is the AI response to the prompt"
        assert result.reasoning == "Test reasoning"
        assert result.scores.truthseeker == 0.8
        assert result.scores.panderer == 0.1
        assert result.scores.convincer == 0.1
        assert result.first_model == "gpt-3.5-turbo"
        assert result.second_model == "gpt-4o"
        
        # Verify both API calls were made
        assert mock_call_ai.call_count == 2