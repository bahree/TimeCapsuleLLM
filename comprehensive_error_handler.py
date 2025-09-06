#!/usr/bin/env python3
"""
Comprehensive Error Handling System for London Historical Data Downloader
Provides robust error handling, logging, and recovery mechanisms
"""

import os
import sys
import logging
import traceback
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
import functools
import time
import requests
from requests.exceptions import RequestException, Timeout, ConnectionError, HTTPError

class ComprehensiveErrorHandler:
    def __init__(self, log_dir="logs", max_retries=3, retry_delay=1):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        # Error tracking
        self.error_counts = {}
        self.error_history = []
        self.recovery_attempts = {}
        
        # Setup comprehensive logging
        self._setup_logging()
        
        # Error categories
        self.error_categories = {
            'network': ['ConnectionError', 'Timeout', 'HTTPError', 'RequestException'],
            'file': ['FileNotFoundError', 'PermissionError', 'OSError', 'IOError'],
            'data': ['ValueError', 'TypeError', 'KeyError', 'AttributeError'],
            'xml': ['ET.ParseError', 'xml.etree.ElementTree.ParseError'],
            'json': ['json.JSONDecodeError', 'json.JSONEncoder'],
            'system': ['MemoryError', 'SystemError', 'RuntimeError']
        }
    
    def _setup_logging(self):
        """Setup comprehensive logging system"""
        # Create loggers for different components
        self.loggers = {
            'main': self._create_logger('main', 'main.log'),
            'network': self._create_logger('network', 'network.log'),
            'data': self._create_logger('data', 'data_processing.log'),
            'errors': self._create_logger('errors', 'errors.log'),
            'recovery': self._create_logger('recovery', 'recovery.log')
        }
        
        # Main logger for general use
        self.logger = self.loggers['main']
    
    def _create_logger(self, name: str, filename: str) -> logging.Logger:
        """Create a logger with file and console handlers"""
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        
        # File handler
        file_handler = logging.FileHandler(self.log_dir / filename)
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def categorize_error(self, error: Exception) -> str:
        """Categorize an error based on its type"""
        error_type = type(error).__name__
        
        for category, error_types in self.error_categories.items():
            if error_type in error_types:
                return category
        
        return 'unknown'
    
    def log_error(self, error: Exception, context: str = "", level: str = "ERROR") -> Dict[str, Any]:
        """Log an error with full context and categorization"""
        error_info = {
            'timestamp': datetime.now().isoformat(),
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context,
            'category': self.categorize_error(error),
            'traceback': traceback.format_exc(),
            'level': level
        }
        
        # Log to appropriate logger
        if level == "CRITICAL":
            self.loggers['errors'].critical(f"{context}: {error}")
        elif level == "ERROR":
            self.loggers['errors'].error(f"{context}: {error}")
        elif level == "WARNING":
            self.loggers['errors'].warning(f"{context}: {error}")
        else:
            self.loggers['errors'].info(f"{context}: {error}")
        
        # Update error counts
        error_key = f"{error_info['category']}:{error_info['error_type']}"
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
        
        # Add to error history
        self.error_history.append(error_info)
        
        # Keep only last 1000 errors
        if len(self.error_history) > 1000:
            self.error_history = self.error_history[-1000:]
        
        return error_info
    
    def retry_with_backoff(self, func: Callable, *args, **kwargs) -> Any:
        """Retry a function with exponential backoff"""
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_error = e
                error_info = self.log_error(
                    e, 
                    f"Attempt {attempt + 1}/{self.max_retries} failed for {func.__name__}",
                    "WARNING"
                )
                
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (2 ** attempt)
                    self.logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    self.log_error(
                        last_error,
                        f"All {self.max_retries} attempts failed for {func.__name__}",
                        "ERROR"
                    )
        
        raise last_error
    
    def handle_network_error(self, error: Exception, url: str = "") -> Dict[str, Any]:
        """Handle network-related errors with specific recovery strategies"""
        error_info = self.log_error(error, f"Network error for URL: {url}", "ERROR")
        
        recovery_strategies = {
            'ConnectionError': 'Check internet connection and retry',
            'Timeout': 'Increase timeout and retry',
            'HTTPError': 'Check URL validity and server status',
            'RequestException': 'Check request parameters and retry'
        }
        
        error_type = type(error).__name__
        strategy = recovery_strategies.get(error_type, 'General network troubleshooting')
        
        recovery_info = {
            'error_info': error_info,
            'recovery_strategy': strategy,
            'suggested_actions': [
                'Check internet connection',
                'Verify URL is accessible',
                'Check firewall settings',
                'Try again later if server is down'
            ]
        }
        
        self.loggers['recovery'].info(f"Network error recovery: {strategy}")
        return recovery_info
    
    def handle_file_error(self, error: Exception, file_path: str = "") -> Dict[str, Any]:
        """Handle file-related errors with specific recovery strategies"""
        error_info = self.log_error(error, f"File error for: {file_path}", "ERROR")
        
        recovery_strategies = {
            'FileNotFoundError': 'Check file path and create directory if needed',
            'PermissionError': 'Check file permissions and run with appropriate privileges',
            'OSError': 'Check disk space and file system',
            'IOError': 'Check file accessibility and format'
        }
        
        error_type = type(error).__name__
        strategy = recovery_strategies.get(error_type, 'General file troubleshooting')
        
        recovery_info = {
            'error_info': error_info,
            'recovery_strategy': strategy,
            'suggested_actions': [
                'Check file path exists',
                'Verify file permissions',
                'Check disk space',
                'Ensure file is not locked by another process'
            ]
        }
        
        self.loggers['recovery'].info(f"File error recovery: {strategy}")
        return recovery_info
    
    def handle_data_error(self, error: Exception, data_type: str = "") -> Dict[str, Any]:
        """Handle data processing errors with specific recovery strategies"""
        error_info = self.log_error(error, f"Data processing error for: {data_type}", "ERROR")
        
        recovery_strategies = {
            'ValueError': 'Check data format and validation',
            'TypeError': 'Check data types and conversions',
            'KeyError': 'Check data structure and required keys',
            'AttributeError': 'Check object structure and methods'
        }
        
        error_type = type(error).__name__
        strategy = recovery_strategies.get(error_type, 'General data troubleshooting')
        
        recovery_info = {
            'error_info': error_info,
            'recovery_strategy': strategy,
            'suggested_actions': [
                'Validate input data format',
                'Check data structure',
                'Verify required fields are present',
                'Handle missing or malformed data gracefully'
            ]
        }
        
        self.loggers['recovery'].info(f"Data error recovery: {strategy}")
        return recovery_info
    
    def handle_xml_error(self, error: Exception, xml_file: str = "") -> Dict[str, Any]:
        """Handle XML parsing errors with specific recovery strategies"""
        error_info = self.log_error(error, f"XML parsing error for: {xml_file}", "ERROR")
        
        recovery_strategies = {
            'ET.ParseError': 'Check XML format and encoding',
            'xml.etree.ElementTree.ParseError': 'Validate XML structure and namespaces'
        }
        
        error_type = type(error).__name__
        strategy = recovery_strategies.get(error_type, 'General XML troubleshooting')
        
        recovery_info = {
            'error_info': error_info,
            'recovery_strategy': strategy,
            'suggested_actions': [
                'Validate XML format',
                'Check encoding (UTF-8)',
                'Verify XML structure',
                'Check for malformed tags or attributes'
            ]
        }
        
        self.loggers['recovery'].info(f"XML error recovery: {strategy}")
        return recovery_info
    
    def handle_json_error(self, error: Exception, json_file: str = "") -> Dict[str, Any]:
        """Handle JSON processing errors with specific recovery strategies"""
        error_info = self.log_error(error, f"JSON processing error for: {json_file}", "ERROR")
        
        recovery_strategies = {
            'json.JSONDecodeError': 'Check JSON format and syntax',
            'json.JSONEncoder': 'Check data types for JSON serialization'
        }
        
        error_type = type(error).__name__
        strategy = recovery_strategies.get(error_type, 'General JSON troubleshooting')
        
        recovery_info = {
            'error_info': error_info,
            'recovery_strategy': strategy,
            'suggested_actions': [
                'Validate JSON syntax',
                'Check for proper escaping',
                'Verify data types',
                'Handle null or undefined values'
            ]
        }
        
        self.loggers['recovery'].info(f"JSON error recovery: {strategy}")
        return recovery_info
    
    def create_error_report(self) -> Dict[str, Any]:
        """Create a comprehensive error report"""
        report = {
            'generated_at': datetime.now().isoformat(),
            'total_errors': len(self.error_history),
            'error_counts_by_category': {},
            'error_counts_by_type': {},
            'recent_errors': self.error_history[-10:],  # Last 10 errors
            'error_trends': self._analyze_error_trends(),
            'recovery_suggestions': self._generate_recovery_suggestions()
        }
        
        # Count errors by category
        for error_info in self.error_history:
            category = error_info['category']
            report['error_counts_by_category'][category] = report['error_counts_by_category'].get(category, 0) + 1
        
        # Count errors by type
        for error_info in self.error_history:
            error_type = error_info['error_type']
            report['error_counts_by_type'][error_type] = report['error_counts_by_type'].get(error_type, 0) + 1
        
        return report
    
    def _analyze_error_trends(self) -> Dict[str, Any]:
        """Analyze error trends over time"""
        if len(self.error_history) < 2:
            return {'trend': 'insufficient_data'}
        
        # Group errors by hour
        hourly_errors = {}
        for error_info in self.error_history:
            hour = error_info['timestamp'][:13]  # YYYY-MM-DDTHH
            hourly_errors[hour] = hourly_errors.get(hour, 0) + 1
        
        # Calculate trend
        hours = sorted(hourly_errors.keys())
        if len(hours) >= 2:
            recent_avg = sum(hourly_errors[h] for h in hours[-3:]) / min(3, len(hours))
            earlier_avg = sum(hourly_errors[h] for h in hours[:-3]) / max(1, len(hours) - 3)
            
            if recent_avg > earlier_avg * 1.5:
                trend = 'increasing'
            elif recent_avg < earlier_avg * 0.5:
                trend = 'decreasing'
            else:
                trend = 'stable'
        else:
            trend = 'insufficient_data'
        
        return {
            'trend': trend,
            'hourly_distribution': hourly_errors,
            'most_common_category': max(self.error_counts.keys(), key=self.error_counts.get) if self.error_counts else None
        }
    
    def _generate_recovery_suggestions(self) -> List[str]:
        """Generate recovery suggestions based on error patterns"""
        suggestions = []
        
        # Analyze error patterns
        if 'network' in [error['category'] for error in self.error_history[-10:]]:
            suggestions.append("Network issues detected - check internet connection and server status")
        
        if 'file' in [error['category'] for error in self.error_history[-10:]]:
            suggestions.append("File access issues detected - check permissions and disk space")
        
        if 'data' in [error['category'] for error in self.error_history[-10:]]:
            suggestions.append("Data processing issues detected - validate input data format")
        
        if len(self.error_history) > 50:
            suggestions.append("High error rate detected - consider reducing concurrency or adding delays")
        
        return suggestions
    
    def save_error_report(self, filename: str = "error_report.json") -> str:
        """Save error report to file"""
        report = self.create_error_report()
        report_file = self.log_dir / filename
        
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Error report saved: {report_file}")
            return str(report_file)
            
        except Exception as e:
            self.logger.error(f"Failed to save error report: {str(e)}")
            return None
    
    def cleanup_old_logs(self, days_to_keep: int = 7):
        """Clean up old log files"""
        try:
            cutoff_time = time.time() - (days_to_keep * 24 * 60 * 60)
            
            for log_file in self.log_dir.glob("*.log"):
                if log_file.stat().st_mtime < cutoff_time:
                    log_file.unlink()
                    self.logger.info(f"Cleaned up old log: {log_file}")
            
        except Exception as e:
            self.logger.error(f"Error cleaning up logs: {str(e)}")
    
    def get_error_summary(self) -> str:
        """Get a summary of current error status"""
        total_errors = len(self.error_history)
        error_categories = set(error['category'] for error in self.error_history)
        
        summary = f"Error Summary: {total_errors} total errors, {len(error_categories)} categories"
        
        if error_categories:
            summary += f" ({', '.join(error_categories)})"
        
        return summary

def error_handler_decorator(error_handler: ComprehensiveErrorHandler, context: str = ""):
    """Decorator to automatically handle errors in functions"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_handler.log_error(e, f"{context}: {func.__name__}")
                raise
        return wrapper
    return decorator

def main():
    """Test the comprehensive error handler"""
    print("🔧 Comprehensive Error Handler - Test")
    print("=" * 50)
    
    # Initialize error handler
    error_handler = ComprehensiveErrorHandler()
    
    print("✅ Error handler initialized")
    print(f"   Log directory: {error_handler.log_dir}")
    print(f"   Max retries: {error_handler.max_retries}")
    print(f"   Retry delay: {error_handler.retry_delay}")
    
    # Test error logging
    try:
        raise ValueError("Test error for error handler")
    except Exception as e:
        error_handler.log_error(e, "Test error logging")
    
    # Test error report
    report = error_handler.create_error_report()
    print(f"✅ Error report created: {len(report['recent_errors'])} recent errors")
    
    # Save error report
    report_file = error_handler.save_error_report()
    if report_file:
        print(f"✅ Error report saved: {report_file}")
    
    print("\n💡 Error handler ready for use!")
    print("   Use: @error_handler_decorator(error_handler, 'context')")

if __name__ == "__main__":
    main()
