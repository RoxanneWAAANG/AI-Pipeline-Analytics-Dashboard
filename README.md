# AI Pipeline Analytics Dashboard

A comprehensive analytics dashboard for monitoring AI pipeline performance with real-time data visualization, built using serverless AWS architecture and modern web technologies.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Usage](#usage)
- [API Reference](#api-reference)
- [Deployment](#deployment)
- [Monitoring](#monitoring)
- [Performance](#performance)
- [Security](#security)
- [Testing](#testing)
- [Contributing](#contributing)

## Overview

This project implements a production-ready analytics dashboard for monitoring AI pipeline executions. The system provides real-time insights into pipeline performance, success rates, execution times, and query complexity analysis.

### Key Capabilities
- Real-time analytics dashboard with interactive visualizations
- Performance monitoring with response times and success rates
- Advanced query analysis including complexity classification
- AWS integration with DynamoDB, CloudWatch, and Step Functions
- Mock data mode for development and demonstration
- Comprehensive test coverage with automated CI/CD

## Architecture

### System Design

The AI Pipeline implements a serverless microservices architecture:

```
Internet → API Gateway → Lambda Trigger → Step Functions → [4 Lambda Stages] → DynamoDB
                                                ↓
                                        CloudWatch Monitoring
```

### Core Components

#### Pipeline Flow
```
User Request → Input Analysis → AI Processing → Response Enhancement → Logging → Response
```

#### Lambda Functions
- **Input Analyzer**: Analyzes user input characteristics and complexity
- **Response Enhancer**: Enriches responses with metadata and formatting
- **Pipeline Logger**: Stores execution records and performance metrics

#### Data Storage
- **DynamoDB Table**: PipelineLogs with pipeline execution data
- **Primary Key**: pipeline_id (String)
- **Attributes**: timestamp, user_message, analysis, final_response, execution_time_ms, status

#### Monitoring Stack
- **CloudWatch**: Metrics, logs, and dashboards
- **Step Functions Console**: Workflow execution tracking
- **DynamoDB**: Detailed execution logging

## Features

### Dashboard Components
- **Key Metrics**: Total executions, success rates, average response times
- **Execution Timeline**: Pipeline activity over time with complexity breakdown
- **Query Analysis**: Complexity distribution and characteristics analysis
- **Performance Visualization**: Response time patterns and correlations
- **Real-time Monitoring**: Live AWS service monitoring and health status
- **Recent Activity**: Latest execution details and status

### Operating Modes
- **Demo Mode**: Works with simulated data, no AWS required
- **AWS Mode**: Connect to real DynamoDB and CloudWatch data

## Quick Start

Get started in 30 seconds:

```bash
# Clone the repository
git clone <your-repo-url>
cd AI-Pipeline-Analytics-Dashboard

# Install dependencies
pip install -r requirements.txt

# Run the demo
python run_demo_dashboard.py
```

Dashboard URL: http://localhost:8501

## Installation

### Prerequisites
- Python 3.8+
- pip package manager
- AWS CLI (optional, for AWS integration)

### Local Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import analytics_dashboard; print('Installation successful')"
```

### Dependencies
```
streamlit>=1.28.0      # Dashboard framework
plotly>=5.17.0         # Interactive charts
pandas>=2.0.0          # Data manipulation
boto3>=1.34.0          # AWS SDK (optional)
statsmodels>=0.14.0    # Statistical analysis
numpy>=1.24.0          # Numerical computing
```

## Usage

### Running the Dashboard

```bash
# Quick demo with mock data
python run_demo_dashboard.py

# Run directly with Streamlit
streamlit run analytics_dashboard.py

# Full demonstration script
python final_project_demo.py
```

### AWS Configuration (Optional)

```bash
# Configure AWS credentials
aws configure

# Set environment variables
export AWS_REGION=us-east-2
export DYNAMODB_TABLE=PipelineLogs
```

### Dashboard Controls
- **Time Range Selector**: Filter data by hours/days
- **Auto-refresh Toggle**: Enable live updates every 30 seconds
- **Interactive Charts**: Click, zoom, and explore data
- **Export Options**: Download charts and data

## API Reference

### Core Classes

#### AIPipelineAnalytics

```python
from analytics_dashboard import AIPipelineAnalytics

# Initialize analytics client
analytics = AIPipelineAnalytics()
```

#### Key Methods

##### get_pipeline_logs(hours: int = 24) → pd.DataFrame
Retrieves pipeline execution logs from DynamoDB or generates mock data.

```python
# Get last 12 hours of data
df = analytics.get_pipeline_logs(hours=12)
print(f"Retrieved {len(df)} records")
```

##### calculate_performance_metrics(df: pd.DataFrame) → Dict
Calculates key performance metrics from pipeline execution data.

```python
df = analytics.get_pipeline_logs(hours=24)
metrics = analytics.calculate_performance_metrics(df)

print(f"Success Rate: {metrics['success_rate']:.1f}%")
print(f"Avg Response Time: {metrics['avg_response_time']:.0f}ms")
```

##### generate_mock_data(hours: int = 24) → pd.DataFrame
Generates realistic mock data for testing and demonstration.

```python
# Generate mock data for testing
mock_df = analytics.generate_mock_data(hours=48)
print(f"Generated {len(mock_df)} mock records")
```

### Performance Characteristics
- **Data Generation**: O(n) linear complexity
- **Metrics Calculation**: O(n) linear complexity
- **Mock Data Generation**: 1000+ records/second
- **Dashboard Load Time**: <2 seconds

## Deployment

### Local Development
```bash
# Basic setup
pip install -r requirements.txt
python run_demo_dashboard.py
```

### Docker Deployment
```bash
# Build and run with Docker
docker build -t ai-pipeline-analytics .
docker run -p 8501:8501 ai-pipeline-analytics
```

### AWS Production Deployment
```bash
# Deploy to AWS with full integration
./deploy_aws.sh
```

#### Docker Compose
```yaml
version: '3.8'
services:
  analytics-dashboard:
    build: .
    ports:
      - "8501:8501"
    environment:
      - AWS_REGION=us-east-2
      - DYNAMODB_TABLE=PipelineLogs
    restart: unless-stopped
```

### AWS Infrastructure
- **ECS/Fargate**: Container orchestration
- **Application Load Balancer**: Traffic distribution
- **CloudFront**: CDN for global distribution
- **Route 53**: DNS management

## Monitoring

### Key Metrics

#### Step Functions Metrics
- ExecutionsSucceeded: Successful pipeline runs
- ExecutionsFailed: Failed pipeline runs (Alert: >5% of total)
- ExecutionTime: End-to-end execution time (Alert: >30 seconds)

#### Lambda Metrics
- Duration: Function execution time
- Errors: Function error count (Alert: >5 in 5 minutes)
- Invocations: Function invocation count

#### DynamoDB Metrics
- ConsumedReadCapacityUnits: Read operations
- ConsumedWriteCapacityUnits: Write operations
- ThrottledRequests: Rate limiting events (Alert: >0)

### Log Analysis Commands

```bash
# View recent Lambda logs
aws logs filter-log-events \
  --log-group-name /aws/lambda/ai-pipeline-InputAnalyzerFunction \
  --start-time $(date -d '1 hour ago' +%s)000

# Search for errors
aws logs filter-log-events \
  --log-group-name /aws/lambda/ai-pipeline-InputAnalyzerFunction \
  --filter-pattern "ERROR" \
  --start-time $(date -d '24 hours ago' +%s)000
```

### CloudWatch Alarms

```bash
# High error rate alarm
aws cloudwatch put-metric-alarm \
  --alarm-name "AIPipeline-HighErrorRate" \
  --metric-name ExecutionsFailed \
  --namespace AWS/StepFunctions \
  --threshold 5 \
  --comparison-operator GreaterThanThreshold

# High latency alarm
aws cloudwatch put-metric-alarm \
  --alarm-name "AIPipeline-HighLatency" \
  --metric-name ExecutionTime \
  --namespace AWS/StepFunctions \
  --threshold 30000 \
  --comparison-operator GreaterThanThreshold
```

## Performance

### Execution Metrics
- **Average Duration**: 3-5 seconds end-to-end
- **Throughput**: 1000+ concurrent executions
- **Memory Usage**: <50MB base memory
- **Dashboard Load**: <2 seconds

### Stage Breakdown
- Input Analysis: 100-500ms
- AI Processing: 2-3 seconds  
- Response Enhancement: 50-200ms
- Logging: 100-300ms

### Optimization Features
- Smart data caching for performance
- Efficient sorting algorithms
- Resource usage optimization
- Horizontal scaling support

## Testing

### Test Suite
```bash
# Run comprehensive tests
python run_tests.py

# Run with coverage
pytest --cov=analytics_dashboard --cov-report=html

# Performance benchmarks
pytest tests/test_performance.py -v
```

### Test Coverage
- **Target**: 80% minimum coverage
- **Achieved**: 85%+ coverage across all modules
- **Test Types**: Unit, integration, performance, security tests

### CI/CD Pipeline
- **GitHub Actions**: Comprehensive CI/CD pipeline
- **Multi-Python Support**: Testing across Python 3.8-3.11
- **Security Scanning**: Bandit, Safety, Trivy integration
- **Automated Deployment**: Docker build and AWS deployment

## Project Structure

```
AI-Pipeline-Analytics-Dashboard/
├── analytics_dashboard.py      # Main Streamlit dashboard
├── run_demo_dashboard.py       # Quick demo launcher  
├── final_project_demo.py       # Comprehensive demo script
├── run_tests.py               # Test runner
├── coverage_report.py         # Coverage analysis
├── requirements.txt           # Python dependencies
├── pytest.ini               # Test configuration
├── Dockerfile               # Container configuration
├── .gitignore              # Git ignore patterns
├── tests/                  # Test suite
│   ├── test_analytics_dashboard.py
│   └── test_performance.py
├── .github/workflows/      # CI/CD pipeline
│   └── ci.yml
├── chatbot/               # Chatbot integration
└── analytics-env/         # Virtual environment
```
