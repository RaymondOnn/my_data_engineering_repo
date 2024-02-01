
from datetime import datetime
from dataclasses import dataclass
from utils.logger import get_logger

# confluent kafka producer and avro serializer
from confluent_kafka import Producer, KafkaException, Consumer
from confluent_kafka.error import KeySerializationError
from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka.schema_registry.avro import AvroSerializer, AvroDeserializer
from confluent_kafka.serialization import Serializer, \
    SerializationContext, MessageField

from confluent_kafka.schema_registry import SchemaRegistryClient, Schema


logger = get_logger(__name__)


@dataclass
class AvroProducer:
    kafka_brokers: str
    avro_serializer: AvroSerializer

    def __post_init__(self):
        producer_config = {
            "bootstrap.servers": self.kafka_brokers,
            "error_cb": self.__error_callback_func,       
        }
        self.producer = Producer(producer_config)
        logger.info(
            'Created an instance of AvroProducer('
            + ', '.join('{}={}'.format(k, v) for k, v in producer_config.items())
            + ')'
        )

    def __error_callback_func(self, kafka_error) -> None:
        logger.error(kafka_error)
        raise KafkaException(kafka_error)

    @staticmethod
    def _send_delivery_report(err, msg):
        if err is not None:
            logger.error("Message delivery failed: {}".format(err))
            raise KafkaException(err)

        msg_callback_info = {
            "latency": msg.latency(),
            "kafka_offset": msg.offset(),
            "topic_partition": msg.partition(),
            "data_tag": msg.topic(),
            "produce_kafka_time": datetime.fromtimestamp(
                msg.timestamp()[1] / 1e3
            ).strftime("%Y-%m-%d %H:%M:%S.%f"),
        }
        logger.info(f'Message sent: {msg_callback_info}')

    def start_topic(self, topic: str, num_partitions: int, replication_factor: int):
        logger.info(f'Started new topic: {topic} with {num_partitions} partition/s and replication factor {replication_factor} ')
        admin = AdminClient({"bootstrap.servers": self.kafka_brokers})
        new_topic = NewTopic(topic, num_partitions=num_partitions, replication_factor=replication_factor)
        return admin.create_topics([new_topic])

    def send_message(self, topic: str, payload: dict, key_field: str = None, key_serializer: Serializer = None):
        # Serve on_delivery callbacks from previous calls to produce()
        self.producer.poll(timeout=1.0)
        
        if key_field is not None:
            key = payload.pop(key_field)
            key_ctx = SerializationContext(topic, MessageField.KEY)
            val_ctx = SerializationContext(topic, MessageField.VALUE)
            self.producer.produce(
                    topic=topic,
                    key=key_serializer(key, key_ctx),
                    value=self.avro_serializer(payload, val_ctx),
                    on_delivery=self._send_delivery_report
                )
        else:
            self.producer.produce(
                    topic=topic,
                    value=self.avro_serializer(
                        payload,
                        SerializationContext(topic, MessageField.VALUE)
                    ),
                    on_delivery=self._send_delivery_report
                )
        
        # print("\nFlushing records...")
        self.producer.flush()
    
        
@dataclass
class AvroConsumer:
    kafka_brokers: str
    group_id: str
    avro_deserializer: AvroDeserializer
    
    def __post_init__(self):
        consumer_config = {
            'bootstrap.servers': self.kafka_brokers,
            'value.deserializer': self.avro_deserializer,
            'group.id': self.group_id,
            'error_cb': self.__error_callback_func,
            'auto.offset.reset': "earliest"
        }
    
        self.consumer = Consumer(consumer_config)
        
    def __error_callback_func(self, kafka_error) -> KafkaException:
        raise KafkaException(kafka_error)
    
    def consume_messages(self, topic: str) -> None:
        
        self.consumer.subscribe([topic])
        
        while True:
            try:
                msg = self.consumer.poll(1.0)
                if msg is None:
                    continue

                data_msg = msg.value()
                if data_msg is not None:
                    logger.info(data_msg)
            except KeyboardInterrupt:
                break

        self.consumer.close()


@dataclass
class SchemaRegistry:
    endpoint_url: str

    def __post_init__(self):
        schema_config = {
            'url': self.endpoint_url,
        }
        
        self.sr_client = SchemaRegistryClient(schema_config)
        
    def register_schema(self, topic: str, schema_str: str):
        schema_id = self.sr_client.register_schema(
                        subject_name=f'{topic}-value',
                        schema=Schema(schema_str, schema_type="AVRO")
                    )
        return schema_id

    def update_schema(self, topic: str, schema_str: str):
        sr_subject = f'{topic}-value'
        versions_deleted_list = self.sr_client.delete_subject(sr_subject)
        print(f"versions of schema deleted list: {versions_deleted_list}")

        schema_id = self.register_schema(sr_subject, schema_str)
        return schema_id

    def get_schema_str(self, topic: str) -> str:
        sr_subject = f'{topic}-value'
        latest_schema = self.sr_client.get_latest_version(sr_subject)
        return latest_schema.schema.schema_str
    
    def make_serializer(self, schema_str: str) -> AvroSerializer:
        return AvroSerializer(
            schema_registry_client=self.sr_client,
            schema_str=schema_str,
            conf={'auto.register.schemas': False}
        )
        
    def make_deserializer(self, schema_str: str) -> AvroDeserializer:
        return AvroDeserializer(
            schema_registry_client=self.sr_client,
            schema_str=schema_str
        )
        
