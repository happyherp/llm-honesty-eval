"""
Simple configuration management for API keys and basic settings.
"""
import os
import logging
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)


def get_api_key(provider: str) -> Optional[str]:
    """Get API key for a specific provider."""
    key_map = {
        'openai': 'OPENAI_API_KEY',
        'anthropic': 'ANTHROPIC_API_KEY',
        'cohere': 'COHERE_API_KEY',
        'huggingface': 'HUGGINGFACE_API_KEY',
    }
    
    env_var = key_map.get(provider.lower())
    if not env_var:
        logger.warning(f"Unknown provider: {provider}")
        return None
    
    return os.getenv(env_var)


def check_api_keys() -> dict:
    """Check which API keys are available."""
    providers = ['openai', 'anthropic', 'cohere', 'huggingface']
    status = {}
    
    for provider in providers:
        key = get_api_key(provider)
        status[provider] = bool(key)
        if key:
            logger.info(f"{provider.upper()} API key found")
        else:
            logger.warning(f"{provider.upper()} API key not found")
    
    return status


def setup_logging(level: str = "INFO"):
    """Setup basic logging configuration."""
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        force=True  # Override any existing configuration
    )
    
    logger.info(f"Logging configured at {level} level")


# Default models
DEFAULT_FIRST_MODEL = os.getenv('DEFAULT_FIRST_MODEL', 'gpt-3.5-turbo')
DEFAULT_SECOND_MODEL = os.getenv('DEFAULT_SECOND_MODEL', 'gpt-4o')
DEFAULT_TEMPERATURE = float(os.getenv('DEFAULT_TEMPERATURE', '0.7'))
DEFAULT_MAX_TOKENS = int(os.getenv('DEFAULT_MAX_TOKENS', '1000'))

# Setup logging on import
setup_logging(os.getenv('LOG_LEVEL', 'INFO'))