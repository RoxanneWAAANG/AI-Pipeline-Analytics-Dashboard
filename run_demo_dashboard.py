#!/usr/bin/env python3
"""
Quick Demo Script for Analytics Dashboard
Runs the dashboard with sample data without requiring AWS setup
"""

import os
import sys
import subprocess
import json
from datetime import datetime, timedelta
import random

def generate_sample_data():
    """Generate sample data for local testing"""
    print("🔄 Generating sample data for dashboard demo...")
    
    # Sample messages for different complexity levels
    sample_messages = {
        'low': [
            "Hello, how are you?",
            "What is AI?", 
            "Tell me a joke",
            "How does Python work?",
            "What's the weather like?",
            "Can you help me?"
        ],
        'medium': [
            "Can you explain machine learning algorithms?",
            "How do I deploy a web application?",
            "What are the best practices for database design?",
            "Help me understand neural networks",
            "How do I optimize my code performance?",
            "What's the difference between SQL and NoSQL?"
        ],
        'high': [
            "I'm building a distributed microservices architecture with Kubernetes and need help with service mesh implementation, load balancing, and monitoring across multiple clusters.",
            "Can you help me debug this complex machine learning pipeline that processes real-time data streams, applies feature engineering, trains models, and serves predictions with sub-millisecond latency?",
            "I need to implement a real-time analytics system that can handle millions of events per second, process them with Apache Kafka and Spark, and store results in both a data lake and data warehouse.",
            "How do I design a fault-tolerant distributed system with proper circuit breakers, retry mechanisms, and graceful degradation across multiple data centers?"
        ]
    }
    
    # Generate sample pipeline logs
    logs = []
    end_time = datetime.now()
    start_time = end_time - timedelta(days=7)  # 7 days of data
    
    for i in range(150):  # Generate 150 sample records
        # Random timestamp
        time_diff = random.random() * (end_time - start_time).total_seconds()
        timestamp = start_time + timedelta(seconds=time_diff)
        
        # Choose complexity and message
        complexity = random.choices(['low', 'medium', 'high'], weights=[50, 35, 15])[0]
        message = random.choice(sample_messages[complexity])
        
        # Generate realistic metrics based on complexity
        word_count = len(message.split())
        if complexity == 'high':
            exec_time = random.randint(2000, 6000)
        elif complexity == 'medium':
            exec_time = random.randint(800, 2500)
        else:
            exec_time = random.randint(200, 1200)
        
        # Occasional failures (5% failure rate)
        status = 'FAILED' if random.random() < 0.05 else 'SUCCESS'
        
        log_entry = {
            'pipeline_id': f"demo_pipeline_{i:04d}",
            'timestamp': timestamp.isoformat(),
            'user_message': message,
            'analysis': {
                'complexity': complexity,
                'word_count': word_count,
                'has_code': '```' in message or 'def ' in message or 'function' in message,
                'has_question': '?' in message or message.startswith(('What', 'How', 'Why', 'Can'))
            },
            'execution_time_ms': exec_time,
            'status': status
        }
        
        if status == 'FAILED':
            log_entry['error_details'] = random.choice([
                'Timeout exceeded',
                'Service temporarily unavailable', 
                'Rate limit exceeded',
                'Invalid input format'
            ])
        
        logs.append(log_entry)
    
    # Sort by timestamp
    logs.sort(key=lambda x: x['timestamp'])
    
    # Save to local file for potential use
    os.makedirs('logs', exist_ok=True)
    with open('logs/sample_pipeline_logs.json', 'w') as f:
        json.dump(logs, f, indent=2, default=str)
    
    print(f"✅ Generated {len(logs)} sample records")
    return logs

def check_requirements():
    """Check if required packages are installed"""
    required_packages = ['streamlit', 'plotly', 'pandas', 'boto3']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\nInstall them with:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False
    
    return True

def main():
    print("🚀 Advanced Analytics Dashboard - Demo Mode")
    print("=" * 50)
    print()
    
    # Check requirements
    if not check_requirements():
        return
    
    print("✅ All required packages found")
    
    # Generate sample data
    generate_sample_data()
    
    print()
    print("🌟 Starting Analytics Dashboard...")
    print("   → Dashboard will open at: http://localhost:8501")
    print("   → Press Ctrl+C to stop the dashboard")
    print()
    print("💡 This demo runs with simulated data since AWS is not configured.")
    print("   To use real data, configure AWS credentials and DynamoDB.")
    print()
    
    # Run streamlit dashboard
    try:
        subprocess.run([sys.executable, '-m', 'streamlit', 'run', 'analytics_dashboard.py'], 
                      check=True)
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped. Thanks for trying the demo!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running dashboard: {e}")
    except FileNotFoundError:
        print("❌ Streamlit not found. Install it with: pip install streamlit")

if __name__ == "__main__":
    main() 