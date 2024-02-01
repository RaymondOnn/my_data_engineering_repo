
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.decorators import dag, task
from airflow.utils.dates import days_ago
from airflow import settings
from airflow.models import Connection


conn = Connection(
        conn_id='spark_docker'
        conn_type=conn_type,
        host=host,
        login=login,
        password=password,
        port=port
)
session = settings.Session()
session.add(conn)
session.commit()

@dag(start_date=days_ago(0), schedule=None, catchup=False)
def web_streams():
    @task
    def start():
        print("Workflow started...")

    @task
    def end():
        print("Workflow done.")

    run_stream = DockerOperator(
        task_id="web2kafka",
        image="task_web2kafka",
        api_version='auto',
        docker_url="tcp://docker-proxy:2375",
        auto_remove=True,
        command='echo "this is a test message shown from within the container"',
        mount_tmp_dir=False,
        # tty=True,
        network_mode="bridge"
    )

    to_sink = SparkSubmitOperator(
        task_id = 'kafka2pg',
        application = 'spark_script.py',
        conn_id = CONN_ID,
        packages = ("""
            org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,
            org.postgresql:postgresql:42.6.0,
            org.apache.spark:spark-avro_2.12:3.5.0
        """),
        conf= {"spark.pyspark.python": jobs.pex},
        verbose=False
    )


    start() >> run_stream >> to_sink >> end()


web_streams()