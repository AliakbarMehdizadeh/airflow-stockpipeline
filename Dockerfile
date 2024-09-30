# Use the official Airflow image
FROM apache/airflow:2.10.2

# Set the working directory
WORKDIR /opt/airflow

# Switch to the airflow user
USER airflow

# Install additional packages
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Switch back to root for further configuration if needed
USER root

# Copy your DAGs
COPY ./dags /opt/airflow/dags

# Set back to airflow user
USER airflow

