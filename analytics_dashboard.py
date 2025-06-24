import streamlit as st
import boto3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List
import numpy as np
import os

# Configure page
st.set_page_config(
    page_title="AI Pipeline Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

class AIPipelineAnalytics:
    def __init__(self):
        self.use_aws = self.setup_aws_clients()
        if not self.use_aws:
            st.warning("🔧 Running in demo mode with simulated data. Configure AWS credentials to use real data.")
        
    def setup_aws_clients(self):
        """Initialize AWS service clients"""
        try:
            self.dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
            self.cloudwatch = boto3.client('cloudwatch', region_name='us-east-2')
            self.stepfunctions = boto3.client('stepfunctions', region_name='us-east-2')
            self.logs = boto3.client('logs', region_name='us-east-2')
            
            # Test AWS connection
            boto3.client('sts').get_caller_identity()
            return True
        except Exception as e:
            # If AWS fails, we'll use mock data
            return False

    def generate_mock_data(self, hours: int = 24) -> pd.DataFrame:
        """Generate mock data for demo purposes"""
        import random
        from datetime import datetime, timedelta
        
        # Sample data for demonstration
        sample_messages = [
            "How do I implement a REST API in Python?",
            "What's the difference between supervised and unsupervised learning?",
            "Can you help me debug this SQL query?",
            "Explain neural networks in simple terms",
            "How to deploy a machine learning model?",
            "What are the best practices for data preprocessing?",
            "Help me understand Docker containers",
            "How do I optimize database performance?",
            "What's the latest in AI research?",
            "Can you review my Python code?"
        ]
        
        complexities = ['low', 'medium', 'high']
        statuses = ['SUCCESS', 'FAILED']
        
        # Generate random data
        num_records = random.randint(50, 150)
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)
        
        data = []
        for i in range(num_records):
            # Random timestamp within range
            time_diff = random.random() * (end_time - start_time).total_seconds()
            timestamp = start_time + timedelta(seconds=time_diff)
            
            # Random data
            complexity = random.choice(complexities)
            message = random.choice(sample_messages)
            word_count = len(message.split()) + random.randint(0, 20)
            
            # Execution time based on complexity
            if complexity == 'high':
                exec_time = random.randint(2000, 5000)
            elif complexity == 'medium':
                exec_time = random.randint(1000, 3000)
            else:
                exec_time = random.randint(200, 1500)
            
            data.append({
                'pipeline_id': f"pipeline_{i:04d}",
                'timestamp': timestamp,
                'user_message': message,
                'complexity': complexity,
                'word_count': word_count,
                'has_code': random.choice([True, False]),
                'has_question': '?' in message,
                'execution_time_ms': exec_time,
                'status': random.choices(statuses, weights=[95, 5])[0]
            })
        
        return pd.DataFrame(data)

    def get_pipeline_logs(self, hours: int = 24) -> pd.DataFrame:
        """Fetch pipeline execution logs from DynamoDB or generate mock data"""
        if not self.use_aws:
            return self.generate_mock_data(hours)
            
        try:
            table = self.dynamodb.Table('PipelineLogs')
            
            # Calculate time range
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=hours)
            
            # Scan table with time filter
            response = table.scan()
            
            logs = []
            for item in response['Items']:
                try:
                    timestamp = datetime.fromisoformat(item['timestamp'].replace('Z', '+00:00'))
                    if start_time <= timestamp <= end_time:
                        logs.append({
                            'pipeline_id': item['pipeline_id'],
                            'timestamp': timestamp,
                            'user_message': item['user_message'],
                            'complexity': item.get('analysis', {}).get('complexity', 'unknown'),
                            'word_count': item.get('analysis', {}).get('word_count', 0),
                            'has_code': item.get('analysis', {}).get('has_code', False),
                            'has_question': item.get('analysis', {}).get('has_question', False),
                            'execution_time_ms': item.get('execution_time_ms', 0),
                            'status': item.get('status', 'UNKNOWN')
                        })
                except Exception as e:
                    continue
            
            df = pd.DataFrame(logs)
            if df.empty:
                st.info("No data found in DynamoDB. Generating mock data for demonstration.")
                return self.generate_mock_data(hours)
            return df
        except Exception as e:
            st.warning(f"Error fetching from DynamoDB: {str(e)}. Using mock data.")
            return self.generate_mock_data(hours)

    def generate_mock_cloudwatch_metrics(self) -> Dict:
        """Generate mock CloudWatch metrics for demo"""
        import random
        from datetime import datetime, timedelta
        
        metrics = {}
        lambda_functions = ['InputAnalyzerFunction', 'ResponseEnhancerFunction', 'PipelineLoggerFunction']
        
        # Generate mock Lambda metrics
        for function in lambda_functions:
            datapoints = []
            for i in range(24):  # 24 hours of data
                timestamp = datetime.now() - timedelta(hours=23-i)
                datapoints.append({
                    'Timestamp': timestamp,
                    'Average': random.randint(500, 2000),
                    'Maximum': random.randint(2000, 5000),
                    'Minimum': random.randint(100, 500)
                })
            metrics[function] = datapoints
        
        # Mock execution metrics
        metrics['executions_succeeded'] = [
            {'Timestamp': datetime.now() - timedelta(hours=i), 'Sum': random.randint(10, 50)}
            for i in range(24)
        ]
        metrics['executions_failed'] = [
            {'Timestamp': datetime.now() - timedelta(hours=i), 'Sum': random.randint(0, 3)}
            for i in range(24)
        ]
        
        return metrics

    def get_cloudwatch_metrics(self, hours: int = 24) -> Dict:
        """Fetch CloudWatch metrics for pipeline performance"""
        if not self.use_aws:
            return self.generate_mock_cloudwatch_metrics()
            
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=hours)
            
            metrics = {}
            
            # Lambda function metrics
            lambda_functions = ['InputAnalyzerFunction', 'ResponseEnhancerFunction', 'PipelineLoggerFunction']
            
            for function in lambda_functions:
                response = self.cloudwatch.get_metric_statistics(
                    Namespace='AWS/Lambda',
                    MetricName='Duration',
                    Dimensions=[{'Name': 'FunctionName', 'Value': function}],
                    StartTime=start_time,
                    EndTime=end_time,
                    Period=3600,  # 1 hour intervals
                    Statistics=['Average', 'Maximum', 'Minimum']
                )
                metrics[function] = response['Datapoints']
            
            # Step Functions metrics
            response = self.cloudwatch.get_metric_statistics(
                Namespace='AWS/StepFunctions',
                MetricName='ExecutionsSucceeded',
                StartTime=start_time,
                EndTime=end_time,
                Period=3600,
                Statistics=['Sum']
            )
            metrics['executions_succeeded'] = response['Datapoints']
            
            response = self.cloudwatch.get_metric_statistics(
                Namespace='AWS/StepFunctions',
                MetricName='ExecutionsFailed',
                StartTime=start_time,
                EndTime=end_time,
                Period=3600,
                Statistics=['Sum']
            )
            metrics['executions_failed'] = response['Datapoints']
            
            return metrics
        except Exception as e:
            st.warning(f"Error fetching CloudWatch metrics: {str(e)}. Using mock data.")
            return self.generate_mock_cloudwatch_metrics()

    def calculate_performance_metrics(self, df: pd.DataFrame) -> Dict:
        """Calculate key performance indicators"""
        if df.empty:
            return {
                'total_executions': 0,
                'success_rate': 0,
                'avg_response_time': 0,
                'avg_word_count': 0,
                'complexity_distribution': {},
                'code_requests_percentage': 0,
                'question_percentage': 0
            }
        
        try:
            total_executions = len(df)
            
            # Safe calculation with error handling
            if 'status' in df.columns:
                success_rate = len(df[df['status'] == 'SUCCESS']) / total_executions * 100
            else:
                success_rate = 0
                
            if 'execution_time_ms' in df.columns:
                # Convert to numeric, handling invalid values
                execution_times = pd.to_numeric(df['execution_time_ms'], errors='coerce')
                avg_execution_time = execution_times.mean() if not execution_times.isna().all() else 0
            else:
                avg_execution_time = 0
                
            if 'complexity' in df.columns:
                complexity_distribution = df['complexity'].value_counts().to_dict()
            else:
                complexity_distribution = {}
                
            if 'word_count' in df.columns:
                word_counts = pd.to_numeric(df['word_count'], errors='coerce')
                avg_word_count = word_counts.mean() if not word_counts.isna().all() else 0
            else:
                avg_word_count = 0
                
            if 'has_code' in df.columns:
                code_requests_percentage = len(df[df['has_code'] == True]) / total_executions * 100
            else:
                code_requests_percentage = 0
                
            if 'has_question' in df.columns:
                question_percentage = len(df[df['has_question'] == True]) / total_executions * 100
            else:
                question_percentage = 0
            
            return {
                'total_executions': total_executions,
                'success_rate': success_rate,
                'avg_response_time': avg_execution_time,  # For compatibility
                'avg_execution_time': avg_execution_time,
                'avg_word_count': avg_word_count,
                'complexity_distribution': complexity_distribution,
                'code_requests_percentage': code_requests_percentage,
                'question_percentage': question_percentage
            }
            
        except Exception as e:
            # Return safe defaults if calculation fails
            return {
                'total_executions': len(df) if not df.empty else 0,
                'success_rate': 0,
                'avg_response_time': 0,
                'avg_word_count': 0,
                'complexity_distribution': {},
                'code_requests_percentage': 0,
                'question_percentage': 0
            }

def main():
    st.title("🚀 AI Pipeline Analytics Dashboard")
    st.markdown("### Real-time monitoring and analytics for your AI pipeline")
    
    # Initialize analytics
    analytics = AIPipelineAnalytics()
    
    # Sidebar controls
    st.sidebar.title("⚙️ Dashboard Controls")
    time_range = st.sidebar.selectbox(
        "Time Range",
        options=[1, 6, 12, 24, 48, 168],  # hours
        index=3,
        format_func=lambda x: f"Last {x} hours" if x < 24 else f"Last {x//24} days"
    )
    
    auto_refresh = st.sidebar.checkbox("Auto-refresh (30s)", value=False)
    
    if auto_refresh:
        time.sleep(30)
        st.rerun()
    
    # Fetch data
    with st.spinner("Loading pipeline data..."):
        df = analytics.get_pipeline_logs(hours=time_range)
        cloudwatch_metrics = analytics.get_cloudwatch_metrics(hours=time_range)
        performance_metrics = analytics.calculate_performance_metrics(df)
    
    # Main metrics row
    if performance_metrics:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Executions",
                performance_metrics['total_executions'],
                delta=None
            )
        
        with col2:
            st.metric(
                "Success Rate",
                f"{performance_metrics['success_rate']:.1f}%",
                delta=None
            )
        
        with col3:
            st.metric(
                "Avg Response Time",
                f"{performance_metrics['avg_execution_time']:.0f}ms",
                delta=None
            )
        
        with col4:
            st.metric(
                "Avg Word Count",
                f"{performance_metrics['avg_word_count']:.0f}",
                delta=None
            )
    
    # Charts section
    if not df.empty:
        # Execution timeline
        st.subheader("📈 Execution Timeline")
        fig_timeline = px.histogram(
            df,
            x='timestamp',
            color='complexity',
            title="Pipeline Executions Over Time",
            nbins=20
        )
        fig_timeline.update_layout(height=400)
        st.plotly_chart(fig_timeline, use_container_width=True)
        
        # Performance metrics
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🎯 Query Complexity Distribution")
            if performance_metrics.get('complexity_distribution'):
                complexity_df = pd.DataFrame(
                    list(performance_metrics['complexity_distribution'].items()),
                    columns=['Complexity', 'Count']
                )
                fig_complexity = px.pie(
                    complexity_df,
                    values='Count',
                    names='Complexity',
                    title="Query Complexity Breakdown"
                )
                st.plotly_chart(fig_complexity, use_container_width=True)
        
        with col2:
            st.subheader("⚡ Response Time Distribution")
            fig_response_time = px.histogram(
                df,
                x='execution_time_ms',
                title="Response Time Distribution",
                nbins=15
            )
            fig_response_time.update_xaxes(title="Response Time (ms)")
            st.plotly_chart(fig_response_time, use_container_width=True)
        
        # Advanced analytics
        st.subheader("🔍 Advanced Analytics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Query characteristics
            query_characteristics = pd.DataFrame({
                'Characteristic': ['Contains Code', 'Is Question', 'High Complexity'],
                'Percentage': [
                    performance_metrics.get('code_requests_percentage', 0),
                    performance_metrics.get('question_percentage', 0),
                    performance_metrics.get('complexity_distribution', {}).get('high', 0) / performance_metrics.get('total_executions', 1) * 100
                ]
            })
            
            fig_characteristics = px.bar(
                query_characteristics,
                x='Characteristic',
                y='Percentage',
                title="Query Characteristics Analysis"
            )
            st.plotly_chart(fig_characteristics, use_container_width=True)
        
        with col2:
            # Performance correlation
            if len(df) > 1:
                try:
                    # Try to create scatter plot with trendline (requires statsmodels)
                    fig_correlation = px.scatter(
                        df,
                        x='word_count',
                        y='execution_time_ms',
                        color='complexity',
                        title="Word Count vs Response Time Correlation",
                        trendline="ols"
                    )
                except ImportError:
                    # Fallback: scatter plot without trendline
                    fig_correlation = px.scatter(
                        df,
                        x='word_count',
                        y='execution_time_ms',
                        color='complexity',
                        title="Word Count vs Response Time Correlation"
                    )
                st.plotly_chart(fig_correlation, use_container_width=True)
    
    # Real-time monitoring section
    st.subheader("🔄 Real-time System Health")
    
    if cloudwatch_metrics:
        # Lambda performance
        lambda_metrics_df = []
        for function, datapoints in cloudwatch_metrics.items():
            if function.endswith('Function') and datapoints:
                for point in datapoints:
                    lambda_metrics_df.append({
                        'Function': function.replace('Function', ''),
                        'Timestamp': point['Timestamp'],
                        'Duration': point['Average']
                    })
        
        if lambda_metrics_df:
            lambda_df = pd.DataFrame(lambda_metrics_df)
            fig_lambda = px.line(
                lambda_df,
                x='Timestamp',
                y='Duration',
                color='Function',
                title="Lambda Function Performance Trends"
            )
            fig_lambda.update_yaxes(title="Duration (ms)")
            st.plotly_chart(fig_lambda, use_container_width=True)
    
    # Recent executions table
    st.subheader("📋 Recent Executions")
    if not df.empty:
        recent_df = df.sort_values('timestamp', ascending=False).head(10)
        st.dataframe(
            recent_df[['timestamp', 'user_message', 'complexity', 'execution_time_ms', 'status']],
            use_container_width=True
        )
    
    # System alerts
    st.subheader("🚨 System Alerts")
    alerts = []
    
    if performance_metrics:
        if performance_metrics.get('success_rate', 100) < 95:
            alerts.append("⚠️ Success rate below 95%")
        
        if performance_metrics.get('avg_execution_time', 0) > 5000:
            alerts.append("⚠️ Average response time above 5 seconds")
        
        if performance_metrics.get('total_executions', 0) == 0:
            alerts.append("⚠️ No recent pipeline executions")
    
    if alerts:
        for alert in alerts:
            st.warning(alert)
    else:
        st.success("✅ All systems operating normally")

if __name__ == "__main__":
    main() 