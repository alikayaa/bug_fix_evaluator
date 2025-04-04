"""
Configuration utilities module for Bug Fix Evaluator.

This module provides utilities for handling configuration settings.
"""

import os
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

DEFAULT_CONFIG = {
    "log_level": "INFO",
    "work_dir": None,  # Will use a temporary directory if None
    "metrics": {
        "weight_correctness": 0.30,
        "weight_completeness": 0.15,
        "weight_pattern_match": 0.10,
        "weight_cleanliness": 0.15,
        "weight_efficiency": 0.15,
        "weight_complexity": 0.15
    },
    "report": {
        "output_dir": "reports",
        "html_template_path": None,
        "text_template_path": None,
        "markdown_template_path": None
    }
}

def get_default_config() -> Dict[str, Any]:
    """
    Get a copy of the default configuration.
    
    Returns:
        Dictionary with default configuration settings
    """
    return DEFAULT_CONFIG.copy()

def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from a file, with defaults for missing values.
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        Dictionary with configuration settings
    """
    config = DEFAULT_CONFIG.copy()
    
    if config_path and os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                loaded_config = json.load(f)
                
            # Merge loaded config with defaults
            _merge_configs(config, loaded_config)
            
            logger.info(f"Loaded configuration from {config_path}")
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Error loading configuration from {config_path}: {e}")
    
    return config

def save_config(config: Dict[str, Any], config_path: str) -> bool:
    """
    Save configuration to a file.
    
    Args:
        config: Configuration dictionary
        config_path: Path to save the configuration file
        
    Returns:
        True if the configuration was saved successfully, False otherwise
    """
    try:
        # Create parent directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(config_path)), exist_ok=True)
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
            
        logger.info(f"Saved configuration to {config_path}")
        return True
    except (IOError, OSError) as e:
        logger.error(f"Error saving configuration to {config_path}: {e}")
        return False

def get_config_value(config: Dict[str, Any], key: str, default: Any = None) -> Any:
    """
    Get a value from a configuration dictionary, with support for nested keys.
    
    Args:
        config: Configuration dictionary
        key: Key to get, can be nested with dots (e.g., 'metrics.weight_correctness')
        default: Default value to return if the key is not found
        
    Returns:
        Value from the configuration, or the default value if not found
    """
    if '.' in key:
        # Nested key
        parts = key.split('.')
        current = config
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return default
        return current
    else:
        # Simple key
        return config.get(key, default)

def set_config_value(config: Dict[str, Any], key: str, value: Any) -> None:
    """
    Set a value in a configuration dictionary, with support for nested keys.
    
    Args:
        config: Configuration dictionary
        key: Key to set, can be nested with dots (e.g., 'metrics.weight_correctness')
        value: Value to set
    """
    if '.' in key:
        # Nested key
        parts = key.split('.')
        current = config
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        current[parts[-1]] = value
    else:
        # Simple key
        config[key] = value

def _merge_configs(base: Dict[str, Any], override: Dict[str, Any]) -> None:
    """
    Merge two configuration dictionaries, with the override taking precedence.
    
    Args:
        base: Base configuration dictionary (will be modified)
        override: Override configuration dictionary
    """
    for key, value in override.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            # Recursively merge nested dictionaries
            _merge_configs(base[key], value)
        else:
            # Override the value
            base[key] = value

def create_default_config(config_path: str) -> bool:
    """
    Create a default configuration file.
    
    Args:
        config_path: Path to save the configuration file
        
    Returns:
        True if the configuration was created successfully, False otherwise
    """
    return save_config(DEFAULT_CONFIG, config_path)

def validate_config(config: Dict[str, Any]) -> Dict[str, str]:
    """
    Validate a configuration dictionary.
    
    Args:
        config: Configuration dictionary to validate
        
    Returns:
        Dictionary mapping invalid keys to error messages, empty if the configuration is valid
    """
    errors = {}
    
    # Check log level
    log_level = config.get('log_level')
    if log_level and log_level not in ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'):
        errors['log_level'] = f"Invalid log level: {log_level}"
    
    # Check metrics weights
    metrics = config.get('metrics', {})
    total_weight = 0.0
    for key, value in metrics.items():
        if key.startswith('weight_'):
            if not isinstance(value, (int, float)):
                errors[f"metrics.{key}"] = f"Weight must be a number: {value}"
            elif value < 0:
                errors[f"metrics.{key}"] = f"Weight must be non-negative: {value}"
            else:
                total_weight += value
    
    # Check if weights sum to approximately 1.0
    if total_weight > 0 and abs(total_weight - 1.0) > 0.01:
        errors['metrics.weights'] = f"Weights should sum to 1.0, but sum to {total_weight}"
    
    # Check report settings
    report = config.get('report', {})
    output_dir = report.get('output_dir')
    if output_dir and not isinstance(output_dir, str):
        errors['report.output_dir'] = f"Output directory must be a string: {output_dir}"
    
    # Check template paths
    for key in ('html_template_path', 'text_template_path', 'markdown_template_path'):
        path = report.get(key)
        if path and not isinstance(path, str):
            errors[f"report.{key}"] = f"Template path must be a string: {path}"
        elif path and not os.path.exists(path):
            errors[f"report.{key}"] = f"Template file does not exist: {path}"
    
    return errors
