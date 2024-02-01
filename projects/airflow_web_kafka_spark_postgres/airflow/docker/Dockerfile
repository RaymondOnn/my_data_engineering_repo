
# Use the official python
FROM python:3.10.13-slim-bullseye

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV AIRFLOW_HOME=/opt/airflow
ENV PATH=${AIRFLOW_HOME}.local/bin:$PATH

# Include configuration and neccessary files into image
# Set the working directory
WORKDIR ${AIRFLOW_HOME}
COPY airflow.requirements.txt .
#COPY dags .
COPY ../airflow.cfg entrypoint.sh ./
COPY ../../components ./components
# Install system dependencies
# Install Apache Airflow and other python packages from requirements
# Set up a non-root user
# Create the AIRFLOW_HOME directory and set ownership
# Remove unnecessary packages from image(which has high level vulnerability)
RUN apt-get update  \
    && apt-get install -y --no-install-recommends \
        build-essential \
        default-libmysqlclient-dev \
        git \
        curl \
        wget \
        vim \
        netcat \
        libglib2.0-0 \
        ssh \
    && rm -rf /var/lib/apt/lists/*  \
    && mkdir -p $AIRFLOW_HOME \
    && ln -s /usr/bin/python3.8 /usr/bin/python  \
    && pip install -r airflow.requirements.txt  \
    && useradd -ms /bin/bash airflow --uid 50000  \
    && apt-get remove --auto-remove linux-libc-dev -y \
    && chown -R airflow: $AIRFLOW_HOME  \
    && chmod +x ./entrypoint.sh

# Switch to the non-root user
USER airflow

# Expose the necessary ports
EXPOSE 8080 5555 8793

ENTRYPOINT ["./entrypoint.sh"]