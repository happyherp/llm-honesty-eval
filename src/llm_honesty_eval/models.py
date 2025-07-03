"""Pydantic models for structured data validation."""

from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, validator


class HonestyScores(BaseModel):
    """Scores for different honesty patterns."""
    
    truthseeker: float = Field(
        ..., 
        ge=0.0, 
        le=1.0, 
        description="Score for truth-seeking behavior (0-1)"
    )
    panderer: float = Field(
        ..., 
        ge=0.0, 
        le=1.0, 
        description="Score for pandering behavior (0-1)"
    )
    convincer: float = Field(
        ..., 
        ge=0.0, 
        le=1.0, 
        description="Score for convincing behavior (0-1)"
    )
    
    @validator('truthseeker', 'panderer', 'convincer')
    def validate_score_range(cls, v):
        """Ensure scores are between 0 and 1."""
        if not 0.0 <= v <= 1.0:
            raise ValueError('Score must be between 0.0 and 1.0')
        return v


class ModelInfo(BaseModel):
    """Information about an AI model used in evaluation."""
    
    name: str = Field(..., description="Model name (e.g., gpt-3.5-turbo)")
    provider: str = Field(..., description="Provider name (e.g., openai)")
    temperature: float = Field(default=0.7, description="Temperature setting")
    max_tokens: int = Field(default=1000, description="Maximum tokens")


class EvaluationResult(BaseModel):
    """Complete result of an honesty evaluation."""
    
    # Metadata
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    evaluation_id: str = Field(..., description="Unique identifier for this evaluation")
    
    # Input
    original_prompt: str = Field(..., description="The original prompt sent to the first AI")
    first_model: ModelInfo = Field(..., description="Information about the first AI model")
    second_model: ModelInfo = Field(..., description="Information about the evaluating AI model")
    
    # First AI Response
    first_response: str = Field(..., description="Response from the first AI")
    first_response_metadata: Dict[str, Any] = Field(
        default_factory=dict, 
        description="Metadata from first AI call (tokens, timing, etc.)"
    )
    
    # Evaluation
    evaluation_prompt: str = Field(..., description="Prompt sent to the evaluating AI")
    reasoning: str = Field(..., description="AI's reasoning for the evaluation")
    scores: HonestyScores = Field(..., description="Honesty pattern scores")
    evaluation_metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Metadata from evaluation AI call"
    )
    
    # Optional fields
    notes: Optional[str] = Field(None, description="Additional notes or observations")
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ConfigModel(BaseModel):
    """Configuration model for the application."""
    
    # Model settings
    first_model: str = Field(default="gpt-3.5-turbo")
    second_model: str = Field(default="gpt-4o")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=1000, gt=0)
    
    # Logging
    log_level: str = Field(default="INFO")
    log_format: str = Field(default="json")
    
    # Output
    output_format: str = Field(default="json")
    output_file: Optional[str] = Field(None)
    
    @validator('log_level')
    def validate_log_level(cls, v):
        """Validate log level."""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f'Log level must be one of: {valid_levels}')
        return v.upper()
    
    @validator('log_format')
    def validate_log_format(cls, v):
        """Validate log format."""
        valid_formats = ['json', 'text']
        if v.lower() not in valid_formats:
            raise ValueError(f'Log format must be one of: {valid_formats}')
        return v.lower()
    
    @validator('output_format')
    def validate_output_format(cls, v):
        """Validate output format."""
        valid_formats = ['json', 'yaml', 'pretty']
        if v.lower() not in valid_formats:
            raise ValueError(f'Output format must be one of: {valid_formats}')
        return v.lower()