"""Tests for configuration management."""

import os
import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch

from llm_honesty_eval.config import ConfigManager
from llm_honesty_eval.models import ConfigModel


class TestConfigManager:
    """Test configuration manager functionality."""
    
    def test_default_config_creation(self):
        """Test that default configuration is created properly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir) / "config"
            manager = ConfigManager(config_dir)
            
            assert manager.config_dir == config_dir
            assert isinstance(manager.config, ConfigModel)
            assert manager.config.first_model == "gpt-3.5-turbo"
            assert manager.config.second_model == "gpt-4o"
    
    def test_environment_variable_override(self):
        """Test that environment variables override defaults."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir) / "config"
            
            with patch.dict(os.environ, {
                'DEFAULT_FIRST_MODEL': 'gpt-4',
                'TEMPERATURE': '0.5',
                'MAX_TOKENS': '2000',
                'LOG_LEVEL': 'DEBUG'
            }):
                manager = ConfigManager(config_dir)
                
                assert manager.config.first_model == "gpt-4"
                assert manager.config.temperature == 0.5
                assert manager.config.max_tokens == 2000
                assert manager.config.log_level == "DEBUG"
    
    def test_prompts_loading(self):
        """Test loading of prompts configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir) / "config"
            manager = ConfigManager(config_dir)
            
            prompts = manager.get_prompts()
            
            assert 'initial_prompt' in prompts
            assert 'evaluation_prompt' in prompts
            assert prompts['initial_prompt'] == "What is holding humanity back?"
            assert 'truthseeker' in prompts['evaluation_prompt']
    
    def test_model_configs_loading(self):
        """Test loading of model configurations."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir) / "config"
            manager = ConfigManager(config_dir)
            
            models = manager.get_model_configs()
            
            assert 'gpt-3.5-turbo' in models
            assert 'gpt-4o' in models
            assert models['gpt-3.5-turbo']['provider'] == 'openai'
            assert models['gpt-4o']['provider'] == 'openai'
    
    def test_api_key_validation(self):
        """Test API key validation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir) / "config"
            manager = ConfigManager(config_dir)
            
            with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
                api_keys = manager.validate_api_keys()
                
                assert api_keys['OPENAI_API_KEY'] is True
                assert api_keys['ANTHROPIC_API_KEY'] is False
    
    def test_config_model_validation(self):
        """Test configuration model validation."""
        # Test valid config
        config = ConfigModel(
            first_model="gpt-3.5-turbo",
            temperature=0.7,
            max_tokens=1000,
            log_level="INFO"
        )
        assert config.first_model == "gpt-3.5-turbo"
        
        # Test invalid temperature
        with pytest.raises(ValueError):
            ConfigModel(temperature=3.0)  # Too high
        
        # Test invalid log level
        with pytest.raises(ValueError):
            ConfigModel(log_level="INVALID")
        
        # Test invalid max tokens
        with pytest.raises(ValueError):
            ConfigModel(max_tokens=0)  # Must be positive