"""Centralized application configuration"""
from dataclasses import dataclass, field
from pathlib import Path
import os
from typing import Optional

@dataclass
class AppConfig:
    """Application configuration with env var support"""
    groq_api_key: str = field(default_factory=lambda: os.getenv("GROQ_API_KEY", ""))
    default_model: str = os.getenv("DEFAULT_MODEL", "llama-3.3-70b-versatile")
    max_slides: int = int(os.getenv("MAX_SLIDES", "50"))
    default_slides: int = int(os.getenv("DEFAULT_SLIDES", "10"))
    cache_dir: Path = Path(os.getenv("CACHE_DIR", ".cache"))
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def from_file(cls, path: str = "config.yaml") -> "AppConfig":
        """Load config from YAML with env var overrides"""
        import yaml
        config_path = Path(path)
        file_config = {}
        
        if config_path.exists():
            try:
                with open(config_path) as f:
                    file_config = yaml.safe_load(f) or {}
            except:
                pass  # Use defaults if file read fails
        
        # Env vars take precedence
        return cls(
            groq_api_key=os.getenv("GROQ_API_KEY", file_config.get("groq_api_key", "")),
            default_model=os.getenv("DEFAULT_MODEL", file_config.get("default_model", cls.default_model)),
            max_slides=int(os.getenv("MAX_SLIDES", file_config.get("max_slides", cls.max_slides))),
            default_slides=int(os.getenv("DEFAULT_SLIDES", file_config.get("default_slides", cls.default_slides))),
            cache_dir=Path(os.getenv("CACHE_DIR", file_config.get("cache_dir", cls.cache_dir))),
            log_level=os.getenv("LOG_LEVEL", file_config.get("log_level", cls.log_level)),
        )
