"""
Logger Wrapper - Centralized logging configuration for the application.

This module provides a singleton logger instance with both console and file handlers,
configured with rotating file support and customizable log levels via environment variables.
"""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional


class LoggerWrapper:
    """
    Wrapper class for centralized logging configuration.
    
    Provides a singleton logger instance with:
    - StreamHandler for terminal output
    - RotatingFileHandler for file logging (5MB max, 3 backups)
    - Configurable log level via LOG_LEVEL environment variable
    - Consistent formatting across all handlers
    """
    
    _instance: Optional['LoggerWrapper'] = None
    _logger: Optional[logging.Logger] = None
    
    def __new__(cls) -> 'LoggerWrapper':
        """Singleton pattern implementation."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self) -> None:
        """Initialize the logger wrapper with handlers and formatters."""
        if self._logger is not None:
            return
        
        # Create logger
        self._logger = logging.getLogger("frenchtalkia")
        
        # Set log level from environment variable (default: INFO)
        log_level_str = os.getenv("LOG_LEVEL", "INFO").upper()
        log_level = getattr(logging, log_level_str, logging.INFO)
        self._logger.setLevel(log_level)
        
        # Prevent propagation to root logger to avoid duplicate logs
        self._logger.propagate = False
        
        # Define log format: [DATA-HORA] [LEVEL] [ARQUIVO:LINHA] - MENSAGEM
        log_format = "[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)d] - %(message)s"
        date_format = "%Y-%m-%d %H:%M:%S"
        formatter = logging.Formatter(log_format, datefmt=date_format)
        
        # Configure StreamHandler for terminal output
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setLevel(log_level)
        stream_handler.setFormatter(formatter)
        self._logger.addHandler(stream_handler)
        
        # Configure RotatingFileHandler for file logging
        log_file_path = Path("app.log")
        file_handler = RotatingFileHandler(
            filename=log_file_path,
            maxBytes=5 * 1024 * 1024,  # 5 MB
            backupCount=3,
            encoding="utf-8"
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        self._logger.addHandler(file_handler)
    
    def _get_logger(self) -> logging.Logger:
        """
        Get the underlying logger instance.
        
        Returns:
            logging.Logger: The initialized logger instance
        """
        if self._logger is None:
            raise RuntimeError("Logger not initialized. Call __init__ first.")
        return self._logger
    
    @property
    def logger(self) -> logging.Logger:
        """Get the underlying logger instance."""
        return self._get_logger()
    
    def debug(self, msg: str) -> None:
        """
        Log a debug message.
        
        Args:
            msg: Message to log
        """
        self._get_logger().debug(msg)
    
    def info(self, msg: str) -> None:
        """
        Log an info message.
        
        Args:
            msg: Message to log
        """
        self._get_logger().info(msg)
    
    def warning(self, msg: str) -> None:
        """
        Log a warning message.
        
        Args:
            msg: Message to log
        """
        self._get_logger().warning(msg)
    
    def error(self, msg: str) -> None:
        """
        Log an error message.
        
        Args:
            msg: Message to log
        """
        self._get_logger().error(msg)
    
    def critical(self, msg: str) -> None:
        """
        Log a critical message.
        
        Args:
            msg: Message to log
        """
        self._get_logger().critical(msg)
    
    def exception(self, msg: str) -> None:
        """
        Log an exception message with traceback.
        
        This method automatically captures the current exception traceback.
        
        Args:
            msg: Message to log
        """
        self._get_logger().exception(msg)


# Singleton instance
logger = LoggerWrapper()
