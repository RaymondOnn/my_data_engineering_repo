try:
    # imports for kafka producer
    from dataclasses import dataclass
    import json
    import os
    import sys

    import yaml
    import py_avro_schema as pas
    from confluent_kafka.serialization import StringSerializer

    from helper.scraper import StaticScraper
    from helper.kafka import AvroProducer, SchemaRegistry
    from helper.logger import get_logger
except Exception as e:
    print(f'Error: {e}')

logger = get_logger('web2kafka')


# TODO: Link classes to web scraper output
@dataclass
class Book:
    stock: str
    title: str
    # sku: str
    rating: str
    price: str


class InvalidConfig(Exception):
    pass


def load_config(filename: str):
    try:
        with open(filename, "r", encoding="utf-8") as file:
            return yaml.safe_load(file)
    except (yaml.scanner.ScannerError, FileNotFoundError) as e:
        raise InvalidConfig(e)


def generate_avro_schema(obj):
    schema_str = pas.generate(
        obj,
        options=pas.Option.JSON_INDENT_2 | pas.Option.NO_AUTO_NAMESPACE
    ).decode()
    # with open('./jobs/nrt/backpacks.avsc', 'w') as f:
    #     json.dump(schema_str, f)
    return schema_str


def fetch_results(scraper, page_header=None):
    resp = scraper.fetch_response(page_header)
    product_links = scraper.get_nodes(resp, 'article.product_pod > h3 a')
    product_headers = {link.attrs['href'] for link in product_links}
    yield from product_headers

    page_header = scraper.get_value(resp, 'href', 'ul.pager > li.next a', 0)
    page_header = '/'.join(['catalogue', page_header.split('/')[-1]])

    # Pagination via recursion: {'href': 'catalogue/page-2.html'}
    if page_header is not None:
        logger.info(f'Proceeding to {page_header}...')
        yield from fetch_results(scraper, page_header)


def fetch_product(scraper, page_header=None):
    ratings = {'one': '1', 'two': '2', 'three': '3', 'four': '4', 'five': '5'}
    resp = scraper.fetch_response(page_header)
    yield {
        "stock": scraper.get_value(resp, 'text', 'table.table-striped tr:nth-child(6) > td', 0),
        "sku": scraper.get_value(resp, 'text', 'table.table-striped tr:nth-child(6) > td', 0),
        "rating": ratings[scraper.get_value(resp, 'class', 'p.star-rating', 0).split()[1].lower()],
        "price": scraper.get_value(resp, 'text', 'p.price_color', 0)[1:],
        "title": scraper.get_value(resp, 'text', 'div.product_main > h1', 0)
    }


def main():
    try:
        workdir = os.path.dirname(os.path.abspath(__file__))
        conf = load_config(os.path.join(workdir, 'config.yaml'))
    except InvalidConfig as err:
        logger.error('Config file failed to load', err)
        return 1

    # Set up schema   How to overwrite schema?
    schema_str = generate_avro_schema(Book)
    sr = SchemaRegistry(endpoint_url=conf['schema_registry']['url'])
    sr.register_schema(conf['kafka']['topic'], schema_str)

    # Set up stream
    producer = AvroProducer(
        kafka_brokers=conf['kafka']['bootstrap_servers'],
        avro_serializer=sr.make_serializer(schema_str))
    producer.start_topic(
        topic=conf['kafka']['topic'],
        num_partitions=2,
        replication_factor=3
    )

    logger.info("Streaming records...")
    scraper = StaticScraper(
        url=conf['webscraper']['base_url'],
        headers=conf['webscraper']['headers']
    )
    for result in fetch_results(scraper):
        result = 'catalogue/' + result.split('catalogue/')[-1]
        for product in fetch_product(scraper, result):
            producer.send_message(
                topic=conf['kafka']['topic'],
                payload=product,
                key_field='sku',
                key_serializer=StringSerializer()
            )


if __name__ == '__main__':
    sys.exit(main())
