import unittest
import time
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import psutil
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import analytics_dashboard

class TestPerformanceBenchmarks(unittest.TestCase):
    """Performance benchmarking tests for AI Pipeline Analytics"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.analytics = analytics_dashboard.AIPipelineAnalytics()
        self.process = psutil.Process(os.getpid())
        
    def benchmark_function(self, func, *args, **kwargs):
        """Benchmark a function and return execution time and memory usage"""
        # Measure initial memory
        initial_memory = self.process.memory_info().rss
        
        # Measure execution time
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        # Measure final memory
        final_memory = self.process.memory_info().rss
        
        return {
            'result': result,
            'execution_time': end_time - start_time,
            'memory_used': final_memory - initial_memory,
            'initial_memory': initial_memory,
            'final_memory': final_memory
        }
        
    def test_mock_data_generation_performance(self):
        """Benchmark mock data generation performance - O(n) complexity"""
        print("\n=== Mock Data Generation Performance ===")
        
        sizes = [10, 100, 500, 1000]
        results = []
        
        for size in sizes:
            # Calculate hours needed for approximately 'size' records
            hours = max(1, size // 10)
            
            benchmark = self.benchmark_function(
                self.analytics.generate_mock_data, 
                hours=hours
            )
            
            df = benchmark['result']
            records = len(df) if not df.empty else 0
            
            results.append({
                'target_size': size,
                'actual_records': records,
                'execution_time': benchmark['execution_time'],
                'memory_used': benchmark['memory_used'],
                'time_per_record': benchmark['execution_time'] / max(records, 1)
            })
            
            print(f"Size: {size:4d} | Records: {records:4d} | "
                  f"Time: {benchmark['execution_time']:.3f}s | "
                  f"Memory: {benchmark['memory_used']/1024/1024:.1f}MB | "
                  f"Time/Record: {benchmark['execution_time']/max(records, 1)*1000:.2f}ms")
        
        # Verify O(n) complexity - time should scale roughly linearly
        if len(results) >= 2:
            time_ratios = []
            for i in range(1, len(results)):
                if results[i-1]['actual_records'] > 0:
                    size_ratio = results[i]['actual_records'] / results[i-1]['actual_records']
                    time_ratio = results[i]['execution_time'] / results[i-1]['execution_time']
                    time_ratios.append(time_ratio / size_ratio)
            
            # Average ratio should be close to 1 for O(n) complexity
            if time_ratios:
                avg_ratio = np.mean(time_ratios)
                print(f"Average time complexity ratio: {avg_ratio:.2f} (closer to 1.0 = better O(n))")
                
                # Allow some variance but should be roughly linear
                self.assertLess(avg_ratio, 3.0, "Data generation appears to be worse than O(n)")
                
        # Performance thresholds
        for result in results:
            self.assertLess(result['time_per_record'], 0.01, 
                          f"Too slow: {result['time_per_record']*1000:.2f}ms per record")
                          
    def test_metrics_calculation_performance(self):
        """Benchmark metrics calculation performance - O(n) complexity"""
        print("\n=== Metrics Calculation Performance ===")
        
        dataset_sizes = [100, 500, 1000, 2000]
        results = []
        
        for size in dataset_sizes:
            # Generate test dataset
            test_data = {
                'execution_time_ms': np.random.randint(100, 5000, size),
                'status': np.random.choice(['SUCCESS', 'FAILED'], size, p=[0.95, 0.05]),
                'word_count': np.random.randint(1, 100, size),
                'complexity': np.random.choice(['low', 'medium', 'high'], size)
            }
            df = pd.DataFrame(test_data)
            
            benchmark = self.benchmark_function(
                self.analytics.calculate_performance_metrics,
                df
            )
            
            results.append({
                'dataset_size': size,
                'execution_time': benchmark['execution_time'],
                'memory_used': benchmark['memory_used'],
                'time_per_record': benchmark['execution_time'] / size
            })
            
            print(f"Size: {size:4d} | Time: {benchmark['execution_time']:.4f}s | "
                  f"Memory: {benchmark['memory_used']/1024:.1f}KB | "
                  f"Time/Record: {benchmark['execution_time']/size*1000000:.2f}μs")
        
        # Verify performance thresholds
        for result in results:
            self.assertLess(result['execution_time'], 1.0, 
                          "Metrics calculation should complete within 1 second")
            self.assertLess(result['time_per_record'], 0.001, 
                          "Should process over 1000 records per second")
                          
    def test_dashboard_load_time(self):
        """Test overall dashboard load time simulation"""
        print("\n=== Dashboard Load Time Simulation ===")
        
        # Simulate dashboard loading process
        start_time = time.time()
        
        # 1. Initialize analytics
        init_time = time.time()
        analytics = analytics_dashboard.AIPipelineAnalytics()
        init_duration = time.time() - init_time
        
        # 2. Generate/load data
        data_time = time.time()
        df = analytics.get_pipeline_logs(hours=24)
        data_duration = time.time() - data_time
        
        # 3. Calculate metrics
        metrics_time = time.time()
        metrics = analytics.calculate_performance_metrics(df)
        metrics_duration = time.time() - metrics_time
        
        # 4. Generate CloudWatch metrics
        cloudwatch_time = time.time()
        cw_metrics = analytics.generate_mock_cloudwatch_metrics()
        cloudwatch_duration = time.time() - cloudwatch_time
        
        total_duration = time.time() - start_time
        
        print(f"Initialization: {init_duration:.3f}s")
        print(f"Data Loading:   {data_duration:.3f}s")
        print(f"Metrics Calc:   {metrics_duration:.3f}s")
        print(f"CloudWatch:     {cloudwatch_duration:.3f}s")
        print(f"Total Load:     {total_duration:.3f}s")
        
        # Dashboard should load within reasonable time
        self.assertLess(total_duration, 5.0, "Dashboard load time should be under 5 seconds")
        self.assertLess(init_duration, 2.0, "Initialization should be under 2 seconds")
        self.assertLess(data_duration, 3.0, "Data loading should be under 3 seconds")
        
    def test_memory_efficiency(self):
        """Test memory usage efficiency and potential memory leaks"""
        print("\n=== Memory Efficiency Test ===")
        
        initial_memory = self.process.memory_info().rss
        peak_memory = initial_memory
        
        # Simulate multiple dashboard refreshes
        for i in range(10):
            # Generate data
            df = self.analytics.generate_mock_data(hours=24)
            
            # Calculate metrics
            metrics = self.analytics.calculate_performance_metrics(df)
            
            # Generate CloudWatch metrics
            cw_metrics = self.analytics.generate_mock_cloudwatch_metrics()
            
            # Check current memory
            current_memory = self.process.memory_info().rss
            if current_memory > peak_memory:
                peak_memory = current_memory
                
            # Clean up references
            del df, metrics, cw_metrics
            
        final_memory = self.process.memory_info().rss
        memory_increase = final_memory - initial_memory
        peak_increase = peak_memory - initial_memory
        
        print(f"Initial Memory: {initial_memory/1024/1024:.1f}MB")
        print(f"Peak Memory:    {peak_memory/1024/1024:.1f}MB (+{peak_increase/1024/1024:.1f}MB)")
        print(f"Final Memory:   {final_memory/1024/1024:.1f}MB (+{memory_increase/1024/1024:.1f}MB)")
        
        # Memory should not grow excessively
        self.assertLess(memory_increase, 50 * 1024 * 1024, 
                       "Memory usage should not increase by more than 50MB")
        self.assertLess(peak_increase, 100 * 1024 * 1024, 
                       "Peak memory should not exceed 100MB increase")
                       
    def test_concurrent_processing_simulation(self):
        """Simulate concurrent processing to test threading behavior"""
        print("\n=== Concurrent Processing Simulation ===")
        
        import threading
        import queue
        
        def worker(analytics, result_queue, worker_id):
            """Worker function for threading test"""
            start_time = time.time()
            try:
                df = analytics.generate_mock_data(hours=12)
                metrics = analytics.calculate_performance_metrics(df)
                execution_time = time.time() - start_time
                result_queue.put({
                    'worker_id': worker_id,
                    'success': True,
                    'execution_time': execution_time,
                    'records': len(df) if not df.empty else 0
                })
            except Exception as e:
                result_queue.put({
                    'worker_id': worker_id,
                    'success': False,
                    'error': str(e),
                    'execution_time': time.time() - start_time
                })
        
        # Test with multiple concurrent workers
        num_workers = 5
        result_queue = queue.Queue()
        threads = []
        
        start_time = time.time()
        
        # Start all workers
        for i in range(num_workers):
            thread = threading.Thread(target=worker, args=(self.analytics, result_queue, i))
            threads.append(thread)
            thread.start()
            
        # Wait for all workers to complete
        for thread in threads:
            thread.join()
            
        total_time = time.time() - start_time
        
        # Collect results
        results = []
        while not result_queue.empty():
            results.append(result_queue.get())
            
        successful_workers = [r for r in results if r['success']]
        failed_workers = [r for r in results if not r['success']]
        
        print(f"Workers: {num_workers}")
        print(f"Successful: {len(successful_workers)}")
        print(f"Failed: {len(failed_workers)}")
        print(f"Total Time: {total_time:.3f}s")
        
        if successful_workers:
            avg_time = np.mean([r['execution_time'] for r in successful_workers])
            print(f"Average Worker Time: {avg_time:.3f}s")
            
        # All workers should succeed
        self.assertEqual(len(failed_workers), 0, f"Failed workers: {failed_workers}")
        
        # Concurrent processing should be reasonably efficient
        self.assertLess(total_time, 10.0, "Concurrent processing should complete within 10 seconds")

class TestScalabilityAnalysis(unittest.TestCase):
    """Analyze system scalability characteristics"""
    
    def test_big_o_analysis(self):
        """Analyze Big O complexity of key operations"""
        print("\n=== Big O Complexity Analysis ===")
        
        analytics = analytics_dashboard.AIPipelineAnalytics()
        
        # Test data generation complexity
        sizes = [50, 100, 200, 400]
        generation_times = []
        
        print("\nData Generation Complexity:")
        for size in sizes:
            hours = max(1, size // 20)  # Approximate hours for target size
            
            start_time = time.time()
            df = analytics.generate_mock_data(hours=hours)
            execution_time = time.time() - start_time
            
            actual_size = len(df) if not df.empty else 0
            generation_times.append((actual_size, execution_time))
            
            print(f"n={actual_size:3d}: {execution_time:.4f}s ({execution_time/actual_size*1000:.2f}ms/record)")
            
        # Analyze complexity trend
        if len(generation_times) >= 2:
            print("\nComplexity Analysis:")
            for i in range(1, len(generation_times)):
                prev_size, prev_time = generation_times[i-1]
                curr_size, curr_time = generation_times[i]
                
                if prev_size > 0 and prev_time > 0:
                    size_ratio = curr_size / prev_size
                    time_ratio = curr_time / prev_time
                    complexity_indicator = time_ratio / size_ratio
                    
                    print(f"  Size ratio: {size_ratio:.2f}, Time ratio: {time_ratio:.2f}, "
                          f"Complexity indicator: {complexity_indicator:.2f}")
                    
                    # For O(n), complexity indicator should be close to 1
                    # For O(n²), it would be close to size_ratio
                    if complexity_indicator < 2.0:
                        print(f"    → Appears to be O(n) - Linear complexity ✓")
                    elif complexity_indicator < size_ratio * 1.5:
                        print(f"    → Appears to be O(n log n) complexity ⚠")
                    else:
                        print(f"    → May be O(n²) or worse complexity ❌")

if __name__ == '__main__':
    unittest.main(verbosity=2) 