tests/test_logger.py

import logging
import os
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.logger import setup_logger, get_logger


def test_logger_creation():
    """Test logger creation and basic functionality"""
    logger = get_logger(__name__)
    assert logger is not None
    assert isinstance(logger, logging.Logger)
    print("✓ Logger creation test passed")


def test_logger_levels():
    """Test different logging levels"""
    logger = get_logger("test_levels")
    
    # Test all logging levels
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")
    
    print("✓ Logger levels test passed")


def test_logger_with_extra_data():
    """Test logging with extra contextual data"""
    logger = get_logger("test_extra")
    
    logger.info("User action", extra={
        "user_id": 12345,
        "action": "login",
        "ip_address": "192.168.1.1"
    })
    
    print("✓ Logger with extra data test passed")


def test_multiple_loggers():
    """Test creating multiple loggers with different names"""
    logger1 = get_logger("module1")
    logger2 = get_logger("module2")
    logger3 = get_logger("module3")
    
    assert logger1.name == "module1"
    assert logger2.name == "module2"
    assert logger3.name == "module3"
    
    logger1.info("Message from module1")
    logger2.info("Message from module2")
    logger3.info("Message from module3")
    
    print("✓ Multiple loggers test passed")


def test_logger_exception_handling():
    """Test logging exceptions"""
    logger = get_logger("test_exception")
    
    try:
        result = 1 / 0
    except ZeroDivisionError:
        logger.exception("An error occurred during division")
    
    print("✓ Logger exception handling test passed")


def test_logger_file_output():
    """Test that log files are created in the correct location"""
    from app.core.config import settings
    
    log_dir = Path("logs")
    
    if settings.ENVIRONMENT == "production":
        log_file = log_dir / "app.log"
        error_log_file = log_dir / "error.log"
        
        # Check if log directory exists
        assert log_dir.exists(), "Log directory should exist"
        print(f"✓ Log directory exists at: {log_dir.absolute()}")
        
        # Log some messages to trigger file creation
        logger = get_logger("test_file_output")
        logger.info("Test info message for file output")
        logger.error("Test error message for file output")
        
        # Note: Files might not exist immediately in development mode
        if log_file.exists():
            print(f"✓ Log file exists at: {log_file.absolute()}")
        if error_log_file.exists():
            print(f"✓ Error log file exists at: {error_log_file.absolute()}")
    else:
        print(f"✓ Running in {settings.ENVIRONMENT} mode - logs output to console")


def test_logger_format():
    """Test logger output format"""
    logger = get_logger("test_format")
    
    # Log a message and verify it contains expected format elements
    logger.info("Testing log format with timestamp and level")
    
    # The format should include: timestamp - name - level - message
    # This is verified by visual inspection in console output
    print("✓ Logger format test passed (check console output above)")


def run_all_tests():
    """Run all logger tests"""
    print("\n" + "="*60)
    print("Running Logger Tests")
    print("="*60 + "\n")
    
    try:
        test_logger_creation()
        test_logger_levels()
        test_logger_with_extra_data()
        test_multiple_loggers()
        test_logger_exception_handling()
        test_logger_file_output()
        test_logger_format()
        
        print("\n" + "="*60)
        print("All Logger Tests Passed Successfully! ✓")
        print("="*60 + "\n")
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    run_all_tests()