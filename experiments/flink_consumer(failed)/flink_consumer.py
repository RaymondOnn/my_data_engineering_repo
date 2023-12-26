from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment
from pathlib import Path

def main():
    BOOTSTRAP_SERVERS = 'localhost:9092, localhost:9093, localhost:9094'
    KAFKA_TOPIC = 'backpacks'
    POSTGRES_USER = 'postgres'
    POSTGRES_PWD = 'postgres'
    POSTGRES_HOST = 'localhost'
    POSTGRES_PORT = '5432'
    POSTGRES_DB_NAME = 'postgres'
    JAR_FILE_PATHS = {
        "kafka": "flink-sql-connector-kafka-1.17.1.jar",
        "jdbc": "flink-connector-jdbc-3.1.0-1.17.jar",
        "postgres": "postgresql-42.6.0.jar"
    }


    # create a streaming TableEnvironment from a StreamExecutionEnvironment
    # env: FlinkContext, t_env: FlinkSession
    env = StreamExecutionEnvironment.get_execution_environment()
    t_env = StreamTableEnvironment.create(env)

    # adding connector jar files
    jar_files = JAR_FILE_PATHS.values()
    t_env.get_config() \
        .set(
            "pipeline.jars",
            ':'.join(['file://' + Path.cwd().joinpath(fname).as_posix() for fname in jar_files])
        )

    # creating new tables in default catalog
    src_ddl = f"""
        CREATE TABLE IF NOT EXISTS source (
            brand STRING,
            title STRING,
            rating DECIMAL(1, 1)
            price DECIMAL(2, 2)
            event_time TIMESTAMP_LTZ(3) METADATA FROM 'timestamp',
            proc_time AS PROCTIME()
        ) WITH (
            'connector' = 'kafka',
            'topic' = '{KAFKA_TOPIC}',
            'properties.bootstrap.servers' = '{BOOTSTRAP_SERVERS}',
            'scan.startup.mode' = 'earliest-offset',
            'format' = 'avro'
        )
    """

    sink_ddl = f"""
        CREATE TABLE IF NOT EXISTS sink (
            brand STRING,
            title STRING,
            rating DECIMAL(1, 1)
            price DECIMAL(2, 2)
            event_time TIMESTAMP_LTZ(3) METADATA FROM 'timestamp',
            proc_time TIMESTAMP
        ) WITH (
            'connector' = 'jdbc',
            'url' = 'jdbc:postgresql://{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB_NAME}',
            'table-name' = 'public.{KAFKA_TOPIC}',
            'user' = '{POSTGRES_USER}',
            'password' = '{POSTGRES_PWD}'
        )
    """

    # Similar concept to Spark's lazy evaluation
    # Need to call an execute method to trigger processing
    t_env.execute_sql(src_ddl)

    # sql_query = execute_sql + return table object
    sink = t_env.sql_query(sink_ddl)

    # get table instance from catalog
    src = t_env.from_path("source")
    # sink = t_env.from_path("sink")

    # write from source to sink
    src.execute_insert("sink").wait()


if __name__ == '__main__':
    main()
