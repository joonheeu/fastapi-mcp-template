"""
Application configuration management with environment variable support.

This module provides centralized configuration management with secure defaults,
environment variable support, and validation for all application settings.
"""

from pydantic_settings import BaseSettings
from pydantic import Field, validator
from typing import Optional, List, Union
import os
import secrets
from pathlib import Path


class Settings(BaseSettings):
    """
    Application settings with environment variable support.
    
    This class handles all configuration for the FastAPI + MCP application,
    including security, database, logging, and service settings.
    """
    
    # App Info
    app_name: str = Field(
        default="My Awesome API",
        description="Application name displayed in docs and logs"
    )
    app_version: str = Field(
        default="0.1.0",
        description="Application version"
    )
    app_description: str = Field(
        default="FastAPI와 MCP를 활용한 API 서버",
        description="Application description for API documentation"
    )
    environment: str = Field(
        default="development",
        description="Current environment (development, production, test)"
    )
    
    # Server Settings
    host: str = Field(
        default="127.0.0.1",
        description="Server host address"
    )
    port: int = Field(
        default=8000,
        ge=1,
        le=65535,
        description="Server port number"
    )
    debug: bool = Field(
        default=True,
        description="Enable debug mode"
    )
    reload: bool = Field(
        default=True,
        description="Enable auto-reload in development"
    )
    
    # MCP Settings
    mcp_host: str = Field(
        default="127.0.0.1",
        description="MCP server host address"
    )
    mcp_port: int = Field(
        default=8001,
        ge=1,
        le=65535,
        description="MCP server port number"
    )
    mcp_transport: str = Field(
        default="sse",
        regex="^(stdio|sse|streamable-http)$",
        description="MCP transport protocol"
    )
    
    # Database Settings (for future use)
    database_url: Optional[str] = Field(
        default=None,
        description="Database connection URL"
    )
    database_echo: bool = Field(
        default=False,
        description="Enable database query logging"
    )
    
    # Security Settings
    secret_key: str = Field(
        default_factory=lambda: secrets.token_urlsafe(32),
        description="Secret key for JWT tokens and encryption"
    )
    algorithm: str = Field(
        default="HS256",
        description="JWT algorithm"
    )
    access_token_expire_minutes: int = Field(
        default=30,
        ge=1,
        description="JWT token expiration time in minutes"
    )
    
    # CORS Settings - More secure defaults
    cors_origins: Union[List[str], str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        description="Allowed CORS origins"
    )
    cors_credentials: bool = Field(
        default=True,
        description="Allow credentials in CORS requests"
    )
    cors_methods: Union[List[str], str] = Field(
        default=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        description="Allowed CORS methods"
    )
    cors_headers: Union[List[str], str] = Field(
        default=["*"],
        description="Allowed CORS headers"
    )
    
    # External APIs
    external_api_url: Optional[str] = Field(
        default=None,
        description="External API base URL"
    )
    external_api_key: Optional[str] = Field(
        default=None,
        description="External API key"
    )
    
    # Logging Settings
    log_level: str = Field(
        default="INFO",
        regex="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$",
        description="Logging level"
    )
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log message format"
    )
    log_file: str = Field(
        default="logs/app.log",
        description="Log file path"
    )
    
    # Testing
    testing: bool = Field(
        default=False,
        description="Enable testing mode"
    )
    
    @validator('cors_origins', pre=True)
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            # Split comma-separated string into list
            return [origin.strip() for origin in v.split(',') if origin.strip()]
        return v
    
    @validator('cors_methods', pre=True)
    def parse_cors_methods(cls, v):
        """Parse CORS methods from string or list."""
        if isinstance(v, str):
            # Split comma-separated string into list
            return [method.strip() for method in v.split(',') if method.strip()]
        return v
    
    @validator('cors_headers', pre=True)
    def parse_cors_headers(cls, v):
        """Parse CORS headers from string or list."""
        if isinstance(v, str):
            # Split comma-separated string into list, or return ["*"] for wildcard
            if v.strip() == "*":
                return ["*"]
            return [header.strip() for header in v.split(',') if header.strip()]
        return v
    
    @validator('secret_key')
    def validate_secret_key(cls, v):
        """Validate that secret key is not the default insecure value."""
        if v == "your-secret-key-change-this-in-production":
            # Generate a secure random key if default is used
            return secrets.token_urlsafe(32)
        if len(v) < 32:
            raise ValueError("Secret key must be at least 32 characters long")
        return v
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment.lower() == "development"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"
    
    @property
    def is_testing(self) -> bool:
        """Check if running in testing environment."""
        return self.environment.lower() == "test" or self.testing
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        # Allow extra fields for flexibility
        extra = "ignore"


class DevelopmentSettings(Settings):
    """
    Development environment settings.
    
    These settings are optimized for local development with enhanced
    debugging capabilities and relaxed security constraints.
    """
    debug: bool = True
    reload: bool = True
    log_level: str = "DEBUG"
    
    # More permissive CORS for development
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001", 
        "http://localhost:8080",
        "http://localhost:8081",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080"
    ]


class ProductionSettings(Settings):
    """
    Production environment settings.
    
    These settings prioritize security and performance for production
    deployments with strict validation and minimal logging.
    """
    debug: bool = False
    reload: bool = False
    log_level: str = "WARNING"
    
    # Strict CORS settings for production
    cors_origins: List[str] = []  # Must be explicitly set via environment
    
    @validator('secret_key')
    def validate_production_secret_key(cls, v):
        """Ensure secret key is properly set in production."""
        if not v or len(v) < 32:
            raise ValueError(
                "SECRET_KEY environment variable must be set with a secure value "
                "of at least 32 characters in production"
            )
        return v
    
    @validator('cors_origins')
    def validate_production_cors(cls, v):
        """Ensure CORS origins are explicitly configured in production."""
        if not v:
            raise ValueError(
                "CORS_ORIGINS must be explicitly configured in production. "
                "Set CORS_ORIGINS environment variable with allowed domains."
            )
        return v


class TestSettings(Settings):
    """
    Test environment settings.
    
    These settings are optimized for automated testing with predictable
    behavior and enhanced logging for debugging test failures.
    """
    debug: bool = True
    testing: bool = True
    log_level: str = "DEBUG"
    
    # Use fixed secret key for consistent testing
    secret_key: str = "test-secret-key-for-testing-purposes-only-32-chars"
    
    # Test database settings
    database_url: str = "sqlite:///./test.db"
    database_echo: bool = True
    
    # Permissive CORS for testing
    cors_origins: List[str] = ["*"]


def get_settings() -> Settings:
    """
    Get settings based on environment.
    
    This function determines the current environment and returns the
    appropriate settings class with environment-specific configurations.
    
    Returns:
        Settings instance for the current environment
        
    Environment Variables:
        ENVIRONMENT: Set to 'development', 'production', or 'test'
        ENV: Alternative to ENVIRONMENT (for backward compatibility)
    """
    # Check both ENVIRONMENT and ENV for flexibility
    env = os.getenv("ENVIRONMENT") or os.getenv("ENV", "development")
    env = env.lower().strip()
    
    if env == "production":
        return ProductionSettings()
    elif env in ("test", "testing"):
        return TestSettings()
    else:
        # Default to development
        return DevelopmentSettings()


# Global settings instance
settings = get_settings()

# Log the configuration being used (for debugging)
import logging
_config_logger = logging.getLogger(__name__)
_config_logger.debug(f"Configuration loaded: {settings.__class__.__name__}")
_config_logger.debug(f"Environment: {settings.environment}")
_config_logger.debug(f"Debug mode: {settings.debug}")


def get_settings_for_testing() -> TestSettings:
    """
    Get test settings explicitly.
    
    This function is useful for dependency injection in tests
    where you want to ensure test settings are used.
    
    Returns:
        TestSettings instance
    """
    return TestSettings() 