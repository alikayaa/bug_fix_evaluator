"""
Tests for the configuration module of the bug fix evaluator.
"""

import os
import sys
import unittest
import tempfile
import json

# Add the src directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from src.bug_fix_evaluator.utils.config import (
    get_default_config,
    load_config,
    save_config,
    get_config_value,
    set_config_value,
    validate_config
)


class TestConfig(unittest.TestCase):
    """Test cases for the configuration module."""
    
    def test_get_default_config(self):
        """Test get_default_config function."""
        config = get_default_config()
        self.assertIsNotNone(config)
        self.assertIn('metrics', config)
        self.assertIn('report', config)
    
    def test_load_save_config(self):
        """Test loading and saving configuration."""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            # Get default config
            config = get_default_config()
            
            # Modify it
            config['log_level'] = 'DEBUG'
            config['metrics']['weight_correctness'] = 0.40
            
            # Save it
            result = save_config(config, tmp_path)
            self.assertTrue(result)
            
            # Load it back
            loaded_config = load_config(tmp_path)
            
            # Check if modification was preserved
            self.assertEqual(loaded_config['log_level'], 'DEBUG')
            self.assertEqual(loaded_config['metrics']['weight_correctness'], 0.40)
        finally:
            # Clean up
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    def test_get_set_config_value(self):
        """Test getting and setting configuration values."""
        config = get_default_config()
        
        # Simple key
        self.assertEqual(get_config_value(config, 'log_level'), 'INFO')
        set_config_value(config, 'log_level', 'DEBUG')
        self.assertEqual(get_config_value(config, 'log_level'), 'DEBUG')
        
        # Nested key
        self.assertEqual(get_config_value(config, 'metrics.weight_correctness'), 0.35)
        set_config_value(config, 'metrics.weight_correctness', 0.40)
        self.assertEqual(get_config_value(config, 'metrics.weight_correctness'), 0.40)
        
        # Non-existent key
        self.assertIsNone(get_config_value(config, 'non_existent'))
        self.assertEqual(get_config_value(config, 'non_existent', 'default'), 'default')
        
        # Setting non-existent nested key
        set_config_value(config, 'new.nested.key', 'value')
        self.assertEqual(get_config_value(config, 'new.nested.key'), 'value')
    
    def test_validate_config(self):
        """Test validating configuration."""
        # Valid config - ensure template paths are None to avoid file existence check
        config = get_default_config()
        config['report']['html_template_path'] = None
        config['report']['text_template_path'] = None
        config['report']['markdown_template_path'] = None
        
        # Fix weights to ensure they sum to 1.0
        config['metrics'] = {
            "weight_correctness": 0.35,
            "weight_completeness": 0.15,
            "weight_pattern_match": 0.10,
            "weight_cleanliness": 0.15,
            "weight_efficiency": 0.10,
            "weight_complexity": 0.15
        }
        
        errors = validate_config(config)
        self.assertEqual(len(errors), 0, f"Validation errors: {errors}")
        
        # Invalid log level
        config['log_level'] = 'INVALID'
        errors = validate_config(config)
        self.assertIn('log_level', errors)
        
        # Invalid weights (not summing to 1.0)
        config['log_level'] = 'INFO'  # Fix previous error
        config['metrics']['weight_correctness'] = 0.5
        config['metrics']['weight_completeness'] = 0.5
        config['metrics']['weight_pattern_match'] = 0.5
        errors = validate_config(config)
        self.assertIn('metrics.weights', errors)


if __name__ == '__main__':
    unittest.main() 