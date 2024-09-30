from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import pandas as pd
from alpha_vantage.timeseries import TimeSeries
from sqlalchemy import create_engine
from datetime import datetime, timedelta

################################################# API ####################################

API_KEY = '04Q03SXFFJPMS0NB'
symbol = 'AAPL'

################################################# EXTRACT ####################################
def fetch_stock_data(symbol):
    ts = TimeSeries(key=API_KEY, output_format='pandas')
    data, _ = ts.get_intraday(symbol=symbol, interval='1min', outputsize='compact')
    return data

def extract():
    # Fetch stock data for AAPL
    return fetch_stock_data(symbol)

################################################# Transform ####################################

def calculate_moving_average(data, window=7):
    data['SMA'] = data['4. close'].rolling(window=window).mean()
    return data

def transform(**context):
    # Get stock data from XCom
    stock_data = context['task_instance'].xcom_pull(task_ids='extract_task')
    # Calculate the moving average
    return calculate_moving_average(stock_data)

################################################# LOAD #######################################

def save_to_db(data, table_name):
    # Connect to PostgreSQL (use the Docker service name 'postgres' if running in Docker Compose)
    engine = create_engine('postgresql://stock_user:stock_pass@postgres:5432/stock_db')
    # Save the data to the database
    data.to_sql(table_name, engine, if_exists='replace')

def load(**context):
    # Get the transformed data from XCom
    transformed_data = context['task_instance'].xcom_pull(task_ids='transform_task')
    # Save to PostgreSQL
    save_to_db(transformed_data, 'apple_stock_data')

################################################# DAGs ####################################

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'start_date': datetime.now() - timedelta(days=1)  # Set start_date to yesterday
}

# Create the DAG
dag = DAG('stock_data_pipeline', default_args=default_args, schedule_interval='@daily')

# Define the tasks
extract_task = PythonOperator(task_id='extract_task', python_callable=extract, dag=dag)
transform_task = PythonOperator(task_id='transform_task', python_callable=transform, dag=dag, provide_context=True)
load_task = PythonOperator(task_id='load_task', python_callable=load, dag=dag, provide_context=True)

# Set task dependencies (ETL)
extract_task >> transform_task >> load_task

