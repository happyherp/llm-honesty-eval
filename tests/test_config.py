"""
Tests for the simplified config module.
"""
import pytest
from unittest.mock import patch
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from common.config import get_api_key, check_api_keys


class TestConfig:
    """Test the config module."""
    
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'})
    def test_get_api_key_found(self):
        """Test getting an API key that exists."""
        key = get_api_key('openai')
        assert key == 'test-key'
    
    @patch.dict(os.environ, {}, clear=True)
    def test_get_api_key_not_found(self):
        """Test getting an API key that doesn't exist."""
        key = get_api_key('openai')
        assert key is None
    
    def test_get_api_key_unknown_provider(self):
        """Test getting an API key for unknown provider."""
        key = get_api_key('unknown')
        assert key is None
    
    @patch.dict(os.environ, {
        'OPENAI_API_KEY': 'openai-key',
        'ANTHROPIC_API_KEY': 'anthropic-key'
    }, clear=True)
    def test_check_api_keys(self):
        """Test checking API key status."""
        status = check_api_keys()
        
        assert status['openai'] is True
        assert status['anthropic'] is True
        assert status['cohere'] is False
        assert status['huggingface'] is False