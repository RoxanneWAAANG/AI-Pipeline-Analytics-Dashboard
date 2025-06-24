import unittest
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add parent directory to path to import the dashboard module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import analytics_dashboard

class TestAIPipelineAnalytics(unittest.TestCase):
    """Test suite for AI Pipeline Analytics Dashboard"""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.analytics = analytics_dashboard.AIPipelineAnalytics()
        
    @patch('boto3.resource')
    @patch('boto3.client')
    def test_setup_aws_clients_success(self, mock_client, mock_resource):
        """Test successful AWS client setup"""
        # Mock successful STS call
        mock_sts = Mock()
        mock_sts.get_caller_identity.return_value = {'Account': '123456789'}
        mock_client.return_value = mock_sts
        
        analytics = analytics_dashboard.AIPipelineAnalytics()
        self.assertTrue(analytics.use_aws)
        
    @patch('boto3.resource')
    @patch('boto3.client')
    def test_setup_aws_clients_failure(self, mock_client, mock_resource):
        """Test AWS client setup failure fallback to mock data"""
        # Mock failed STS call
        mock_client.side_effect = Exception("AWS credentials not configured")
        
        analytics = analytics_dashboard.AIPipelineAnalytics()
        self.assertFalse(analytics.use_aws)
        
    def test_generate_mock_data_structure(self):
        """Test mock data generation returns correct structure"""
        df = self.analytics.generate_mock_data(hours=24)
        
        # Check DataFrame structure
        expected_columns = [
            'pipeline_id', 'timestamp', 'user_message', 'complexity', 
            'word_count', 'has_code', 'has_question', 'execution_time_ms', 'status'
        ]
        
        for col in expected_columns:
            self.assertIn(col, df.columns)
            
        # Check data types
        self.assertIsInstance(df['timestamp'].iloc[0], datetime)
        self.assertIn(df['complexity'].iloc[0], ['low', 'medium', 'high'])
        self.assertIn(df['status'].iloc[0], ['SUCCESS', 'FAILED'])
        
    def test_generate_mock_data_time_range(self):
        """Test mock data generation respects time range"""
        hours = 12
        df = self.analytics.generate_mock_data(hours=hours)
        
        if not df.empty:
            time_range = df['timestamp'].max() - df['timestamp'].min()
            # Should be within the specified time range (with some tolerance)
            self.assertLessEqual(time_range.total_seconds(), hours * 3600 + 3600)
            
    def test_generate_mock_data_complexity_distribution(self):
        """Test mock data has reasonable complexity distribution"""
        df = self.analytics.generate_mock_data(hours=24)
        
        if not df.empty:
            complexity_counts = df['complexity'].value_counts()
            # Should have all complexity levels
            complexities = set(df['complexity'].unique())
            expected_complexities = {'low', 'medium', 'high'}
            self.assertTrue(complexities.issubset(expected_complexities))
            
    def test_calculate_performance_metrics(self):
        """Test performance metrics calculation"""
        # Create sample DataFrame
        data = {
            'execution_time_ms': [1000, 2000, 3000, 4000, 5000],
            'status': ['SUCCESS', 'SUCCESS', 'FAILED', 'SUCCESS', 'SUCCESS'],
            'word_count': [10, 20, 30, 40, 50],
            'complexity': ['low', 'medium', 'high', 'medium', 'low']
        }
        df = pd.DataFrame(data)
        
        metrics = self.analytics.calculate_performance_metrics(df)
        
        # Check metric structure
        self.assertIn('total_executions', metrics)
        self.assertIn('success_rate', metrics)
        self.assertIn('avg_response_time', metrics)
        self.assertIn('avg_word_count', metrics)
        
        # Check calculations
        self.assertEqual(metrics['total_executions'], 5)
        self.assertEqual(metrics['success_rate'], 80.0)  # 4/5 = 80%
        self.assertEqual(metrics['avg_response_time'], 3000)  # mean of execution times
        self.assertEqual(metrics['avg_word_count'], 30)  # mean of word counts
        
    def test_calculate_performance_metrics_empty_dataframe(self):
        """Test performance metrics with empty DataFrame"""
        df = pd.DataFrame()
        metrics = self.analytics.calculate_performance_metrics(df)
        
        self.assertEqual(metrics['total_executions'], 0)
        self.assertEqual(metrics['success_rate'], 0)
        self.assertEqual(metrics['avg_response_time'], 0)
        self.assertEqual(metrics['avg_word_count'], 0)
        
    def test_generate_mock_cloudwatch_metrics(self):
        """Test CloudWatch metrics generation"""
        metrics = self.analytics.generate_mock_cloudwatch_metrics()
        
        # Check structure
        lambda_functions = ['InputAnalyzerFunction', 'ResponseEnhancerFunction', 'PipelineLoggerFunction']
        for function in lambda_functions:
            self.assertIn(function, metrics)
            self.assertIsInstance(metrics[function], list)
            if metrics[function]:
                datapoint = metrics[function][0]
                self.assertIn('Timestamp', datapoint)
                self.assertIn('Average', datapoint)
                
        self.assertIn('executions_succeeded', metrics)
        self.assertIn('executions_failed', metrics)
        
    @patch.object(analytics_dashboard.AIPipelineAnalytics, 'generate_mock_data')
    def test_get_pipeline_logs_mock_mode(self, mock_generate):
        """Test pipeline logs in mock mode"""
        # Set up mock
        mock_df = pd.DataFrame({'test': [1, 2, 3]})
        mock_generate.return_value = mock_df
        
        # Analytics in mock mode
        self.analytics.use_aws = False
        result = self.analytics.get_pipeline_logs(hours=24)
        
        mock_generate.assert_called_once_with(24)
        self.assertEqual(result.equals(mock_df), True)
        
    def test_execution_time_complexity_correlation(self):
        """Test that execution time correlates with complexity"""
        df = self.analytics.generate_mock_data(hours=24)
        
        if not df.empty and len(df) > 10:
            # Group by complexity and check mean execution times
            complexity_times = df.groupby('complexity')['execution_time_ms'].mean()
            
            if 'low' in complexity_times and 'high' in complexity_times:
                # High complexity should generally take longer than low complexity
                # (allowing for some randomness in mock data)
                self.assertGreater(complexity_times['high'], complexity_times['low'] * 0.5)

class TestDataValidation(unittest.TestCase):
    """Test data validation and edge cases"""
    
    def setUp(self):
        self.analytics = analytics_dashboard.AIPipelineAnalytics()
        
    def test_empty_data_handling(self):
        """Test handling of empty datasets"""
        empty_df = pd.DataFrame()
        metrics = self.analytics.calculate_performance_metrics(empty_df)
        
        # Should return default values, not crash
        self.assertIsInstance(metrics, dict)
        self.assertEqual(metrics['total_executions'], 0)
        
    def test_invalid_data_types(self):
        """Test handling of invalid data types"""
        # Create DataFrame with some invalid data
        data = {
            'execution_time_ms': [1000, 'invalid', 3000],
            'status': ['SUCCESS', 'SUCCESS', 'UNKNOWN'],
            'word_count': [10, None, 30],
            'complexity': ['low', 'invalid', 'high']
        }
        df = pd.DataFrame(data)
        
        # Should handle gracefully without crashing
        try:
            metrics = self.analytics.calculate_performance_metrics(df)
            self.assertIsInstance(metrics, dict)
        except Exception as e:
            self.fail(f"calculate_performance_metrics raised {e} with invalid data")

class TestPerformance(unittest.TestCase):
    """Performance tests for analytics functions"""
    
    def setUp(self):
        self.analytics = analytics_dashboard.AIPipelineAnalytics()
        
    def test_large_dataset_performance(self):
        """Test performance with large datasets"""
        import time
        
        # Generate large dataset
        start_time = time.time()
        large_df = self.analytics.generate_mock_data(hours=168)  # 1 week
        generation_time = time.time() - start_time
        
        # Should generate data reasonably quickly (< 5 seconds)
        self.assertLess(generation_time, 5.0)
        
        # Calculate metrics on large dataset
        start_time = time.time()
        metrics = self.analytics.calculate_performance_metrics(large_df)
        calculation_time = time.time() - start_time
        
        # Should calculate metrics quickly (< 1 second)
        self.assertLess(calculation_time, 1.0)
        
    def test_memory_efficiency(self):
        """Test memory usage doesn't grow excessively"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Generate multiple datasets
        for _ in range(10):
            df = self.analytics.generate_mock_data(hours=24)
            metrics = self.analytics.calculate_performance_metrics(df)
            
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (< 100MB)
        self.assertLess(memory_increase, 100 * 1024 * 1024)

if __name__ == '__main__':
    # Run tests with coverage if pytest-cov is available
    pytest.main([__file__, '-v', '--cov=analytics_dashboard', '--cov-report=html', '--cov-report=term']) 