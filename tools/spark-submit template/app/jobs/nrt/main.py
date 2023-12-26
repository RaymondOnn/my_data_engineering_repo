try:
    import sys
    import os
    import yaml
    
    from pyspark import SparkConf
    from pyspark.sql import SparkSession, DataFrame, functions as F
    from pyspark.sql.avro.functions import from_avro
    from confluent_kafka.schema_registry import SchemaRegistryClient
    import time
    # import findspark
    # findspark.init()
except ImportError as e:
    print(f"Error: {e}")

# spark = (
#         SparkSession.builder
#         .master("yarn")
#         .appName("my_spark_application")
#         .config("spark.submit.deployMode", "client")
#         .config("spark.yarn.dist.files", pex_file)
#         .config("spark.executorEnv.PEX_ROOT", "./.pex")
#         .config("spark.sql.shuffle.partitions", 4000)
#         .config("spark.executor.memory", "1G")
#         .enableHiveSupport()
#         .getOrCreate()
#     )
# findspark.init()

# os.environ["PYSPARK_PYTHON"] = "python"
# os.environ["PYSPARK_DRIVER_PYTHON"] = "./environment/bin/python"
#os.environ["PYSPARK_PYTHON"] = sys.executable
#os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

# os.chdir(sys.path[0])
folder_path = os.path.dirname(__file__)
config_file = os.path.join(folder_path, "spark_config.yaml")
with open(config_file, "r", encoding="utf-8") as file:
    config = yaml.safe_load(file)


# Spark config
APP_NAME = config.get("spark").get("app_name")
SPARK_CONFIG = config.get("spark").get("config")
    
# Kafka config
BOOTSTRAP_SERVERS = config.get("kafka").get("bootstrap_servers")
KAFKA_TOPIC = config.get("kafka").get("topic")
KAFKA_CONFIG = config.get("kafka").get("config")

SCHEMA_REGISTRY_URL = config.get("schema_registry").get("url")
SCHEMA_REGISTRY_SUBJECT = f"{KAFKA_TOPIC}-value"

# Postgres config
USER = config.get("postgres").get("user")
PASS = config.get("postgres").get("password")
DB_NAME = config.get("postgres").get("dbname")
SERVER = config.get("postgres").get("server")
PORT = config.get("postgres").get("port")
JDBC_URL = f"jdbc:postgresql://{SERVER}/{DB_NAME}"
TBL_NAME = f"public.{KAFKA_TOPIC}"

# Start SparkSession
# def get_spark_session(app_name: str, config_dict: dict):
#     """Initialize SparkSession

#     Args:
#         app_name (str): Name of pyspark application
#         config_dict (dict): spark configurations supplied in key-value pairs

#     Returns:
#         SparkSession: required entrypoint for spark appications
#     """
#     conf = SparkConf()
#     conf.setAppName(app_name).setAll(config_dict.items())
#     print("SparkSession Created...")
#     pex_file = os.path.basename([path for path in os.listdir(os.getcwd()) if path.endswith(".pex")][0])
#     os.environ["PYSPARK_PYTHON"] = "./" + pex_file
#     # print current PySpark configuration to be sure
#     # print("Current PySpark settings: \n", conf.toDebugString())
#     return SparkSession.builder.config(conf=conf).getOrCreate()


# TODO: Difficulty in bringing external packages into spark cluster
# TODO: Current fix is to share .avsc file
def get_schema(sr_subject: str):
    """Getting avro schema from Schema Registry

    Args:
        sr_subject (str): unique identifier for schema

    Returns:
        str: avro schema definition in JSON format
    """
    schema_str = ""
    sr = SchemaRegistryClient({"url": SCHEMA_REGISTRY_URL})

    print("Requesting for schema...")
    while schema_str == "":
        schema_curr = sr.get_latest_version(sr_subject)
        schema_str = schema_curr.schema.schema_str
        time.sleep(0.5)
    print("Schema Obtained...")
    return schema_str

def fetch_events(spark_session, kafka_topic: str, kafka_config: dict[str, str]) -> DataFrame:
    """Get streaming events from Kafka broker

    Args:
        spark_session (SparkSession): Instance of SparkSession
        kafka_topic (str): Name of Kafka topic
        kafka_config (dict[str, str]): Read configurations for Kafka

    Returns:
        DataFrame: _description_
    """
    print(f'Listening to "{kafka_topic}"...')
    df = spark_session.readStream \
            .format("kafka") \
            .option('kafka.bootstrap.servers', 'kafka-broker-1:9092, kafka-broker-2:9093, kafka-broker-3:9094') \
            .option("subscribe", kafka_topic) \
            .load()
    return df  #.selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)")
            #.options(**kafka_config) \

def avro_bytes_to_table(df: DataFrame, schema_str: str) -> DataFrame:
    """Deserialize avro format and convert events into DataFrame

    Args:
        df (DataFrame): _description_
        schema_str (str): _description_

    Returns:
        DataFrame: _description_
    """
    return df.select(from_avro(F.col("value"), schema_str).alias("value"))

def write_to_postgres(df: DataFrame, batch_id) -> None:
    # will create table before writing if not exists
    df.write \
        .mode("append") \
        .format("jdbc") \
        .option("url", f"jdbc:postgresql://{SERVER}: {PORT}/{DB_NAME}") \
        .option("driver", "org.postgresql.Driver") \
        .option("dbtable", TBL_NAME) \
        .option("user", USER) \
        .option("password", PASS) \
        .save()

def store_events(df: DataFrame):
    """Streams the contents of the DataFrame into postgres

    Args:
        df (DataFrame): Output dataframe

    Returns:
        None
    """
    print("Waiting for Query...")
    sink_df = (
        df.writeStream.foreachBatch(write_to_postgres)
        .outputMode("update")
        .option("checkpointLocation", "chk-point-dir")
        .trigger(processingTime="1 minute")
        .start()
    )
    return sink_df.awaitTermination()

def perform(spark, args):

    test_df = spark.createDataFrame([{"id": 1, "name": "Thomas"}])
    test_df.show()
    #spark = get_spark_session(APP_NAME, SPARK_CONFIG)
    # spark.sparkContext.setLogLevel("ERROR")
    # spark.sparkContext.addPyFile("venv.zip")
    
    # set up kafka source
    src_df = fetch_events(spark, kafka_topic=KAFKA_TOPIC, kafka_config=KAFKA_CONFIG)
    src_df.printSchema()
    src_df.show(2)

    avro_schema = get_schema(SCHEMA_REGISTRY_SUBJECT)
    # avro_schema = open(os.path.join(folder_path, "backpacks.avsc"), mode='r').read()
    print(avro_schema)

    # decode from avro
    decoded_df = avro_bytes_to_table(src_df, avro_schema)mak
    decoded_df.show(2)
    # # TODO: Switch back to schema registry if possible
    # # decoded_df = src_df.select(from_avro(F.col("value"), avro_schema).alias("value"))

    # # write to sink
    # store_events(decoded_df)
    