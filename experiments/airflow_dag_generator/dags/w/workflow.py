from airflow.decorators import dag
from airflow.utils.dates import days_ago
from airflow.operators.bash import BashOperator
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator


@dag(start_date=days_ago(0), schedule=None, catchup=False)
def web_streams():
    task1 = BashOperator(
        task_id='start',
        bash_command='echo "Workflow started at $(date +%Y-%m-%dT%T)"',
    )
    

    run_stream = DockerOperator(
        task_id='web2kafka',
        image='task_web2kafka',
        api_version='auto',
        docker_url='tcp://docker-proxy:2375',
        auto_remove=True,
        command='echo "this is a test message shown from within the container"',
        mount_tmp_dir=False,
        network_mode='bridge',
    )
    

    to_sink = SparkSubmitOperator(
        task_id='kafka2pg',
        application='spark_script.py',
        conn_id='CONN_ID',
        verbose=False,
        packages='org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0, org.postgresql:postgresql:42.6.0, org.apache.spark:spark-avro_2.12:3.5.0',
        conf={'spark.pyspark.python': 'jobs.pex'},
    )
    

    task4 = BashOperator(
        task_id='end',
        bash_command='echo "Workflow finished at $(date +%Y-%m-%dT%T)"',
    )
    

    task1 >> run_stream >> to_sink >> task4


web_streams()
