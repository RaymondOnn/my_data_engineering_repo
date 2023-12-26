try:
    import sys
    import os
    import yaml
    
    from pyspark import SparkConf
    from pyspark.sql import SparkSession, DataFrame, functions as F
    from pyspark.sql.avro.functions import from_avro
    from confluent_kafka.schema_registry import SchemaRegistryClient
except ImportError as e:
    print(f"Error: {e}")

class InvalidConfig(Exception):
    pass

def load_config(filename:str):
    try: 
        with open(filename, "r", encoding="utf-8") as file:
            return yaml.safe_load(file)
    except (yaml.scanner.ScannerError, FileNotFoundError) as e:
        raise InvalidConfig(e)

folder_path = os.path.dirname(__file__)
config_file = os.path.join(folder_path,
                           "spark_config.yaml")
try:
    config = load_config(config_file)
except InvalidConfig as e:
    print('Config file failed to load, e')
    #return 1


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
DB_NAME = config.get("postgres").get("db_name")
SERVER = config.get("postgres").get("server")
PORT = config.get("postgres").get("port")
JDBC_URL = f"jdbc:postgresql://{SERVER}/{DB_NAME}"
TBL_NAME = f"public.{KAFKA_TOPIC}"


def get_spark_session(app_name: str, config_dict: dict):
    """Initialize SparkSession

    Args:
        app_name (str): Name of pyspark application
        config_dict (dict): spark configurations supplied in key-value pairs

    Returns:
        SparkSession: required entrypoint for spark appications
    """
    conf = SparkConf()
    conf.setAppName(app_name).setAll(config_dict.items())
    print("SparkSession Created...")
    pex_file = os.path.basename([path for path in os.listdir(os.getcwd()) if path.endswith(".pex")][0])
    os.environ["PYSPARK_PYTHON"] = "./" + pex_file
    # print current PySpark configuration to be sure
    # print("Current PySpark settings: \n", conf.toDebugString())
    return SparkSession.builder.config(conf=conf).getOrCreate()

def get_schema(sr_subject: str):
    """Getting avro schema from Schema Registry

    Args:
        sr_subject (str): unique identifier for schema

    Returns:
        str: avro schema definition in JSON format
    """
    schema_str = ""
    # if method != 'manual':
    #     return open(os.path.join(folder_path, f"{KAFKA_TOPIC}.avsc"), mode='r').read()
    
    sr = SchemaRegistryClient({"url": SCHEMA_REGISTRY_URL})
    print("Requesting for schema...")
    while schema_str == "":
        schema_curr = sr.get_latest_version(sr_subject)
        schema_str = schema_curr.schema.schema_str
        #time.sleep(0.5)
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
            .options(**kafka_config) \
            .load()
    return df  #.selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)")
def transform(df:DataFrame, schema_str: str) -> DataFrame:
    # 1. Create magic byte column from 1st byte
    # 2. Create schema id from value using next 4 byte
    # 3. remove first 5 bytes from value
    # 4. Deserialize key back to string
    # creating a new df with magicBytes, valueSchemaId & fixedValue
    fromAvroOptions = {"mode":"PERMISSIVE"}
    df = df \
            .withColumn("fixedValue", F.expr("substring(value, 6, length(value)-5)")) \
            .select(from_avro(F.col("fixedValue"), schema_str, fromAvroOptions).alias("value"), "key") \
            .withColumn("key", F.col("key").cast("string").alias("sku")) \
            .select("value.*", "key") \
            .withColumn("rating", F.expr("cast(rating AS int)"))
            # .withColumn("magicByte", F.expr("substring(value, 1, 1)")) \
            # .withColumn("valueSchemaId", F.expr("substring(value, 2, 4)")) \
    return df


def write_to_postgres(df: DataFrame, epoch_id) -> None:
    # will create table before writing if not exists
    df.write \
        .format("jdbc") \
        .option("url", f"jdbc:postgresql://{SERVER}:{PORT}/{DB_NAME}") \
        .option("driver", "org.postgresql.Driver") \
        .option("dbtable", TBL_NAME) \
        .option("user", USER) \
        .option("password", PASS) \
        .mode("append") \
        .save()

def print_to_console(df: DataFrame) -> None:
    df \
        .writeStream \
        .outputMode("append") \
        .format("console") \
        .trigger(processingTime='2 seconds') \
        .start()

def store_events(df: DataFrame):
    """Streams the contents of the DataFrame into postgres

    Args:
        df (DataFrame): Output dataframe

    Returns:
        None
    """
    print("Waiting for Query...")
        # .option("checkpointLocation", "chk-point-dir")
    return df.writeStream \
                .foreachBatch(write_to_postgres) \
                .outputMode("update") \
                .trigger(processingTime="2 seconds") \
                .start()

def perform(spark, args):
    #spark = get_spark_session(APP_NAME, SPARK_CONFIG)
    
    # set up kafka source
    src_df = fetch_events(spark, kafka_topic=KAFKA_TOPIC, kafka_config=KAFKA_CONFIG)
    src_df.printSchema()
    #src_df.show()

    avro_schema = get_schema(SCHEMA_REGISTRY_SUBJECT)
    print(avro_schema)

    # Needs some processing as confluent Avro encoding not compatible with Spark's binary decoder
    # decode from avro
    print('decoding...')
    decoded_df = transform(src_df, avro_schema)
    decoded_df.printSchema()

    # write to sink
    print_to_console(decoded_df)
    sink_df = store_events(decoded_df)
    sink_df.awaitTermination()
    