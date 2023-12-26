# airflow_web_kafka_spark_postgres

### Technical Goals
- Try out tools related to stream processing
- Learn to use `httpx` and `selectolax`
- Figure out how to better deploy Airflow for e.g. less code duplication, automated dags, deploying at scale, error-handling etc

### Learnings
- Web Scraping via `httpx` and `selectolax`
- Automation via `make`files
- The `avro` format
  - Other than the data component, it has an extra schema component that specifies the structure of the data i.e. defines the fields, their data types, default values.
  - The schema is stored in JSON format (in a `.avsc`file)
  - Compared to standard avro format, the Confluent Avro Format has 5 extra bytes added before the avro bytes
    - first byte: magic byte
    - next 4 bytes: schema id
- Packaging python dependencies via pex
  - pex allows for creating a 'portable' virtual environment in which you install all your python dependencies.
  - it creates a `.pex` file which essentially is a zip file that contains the virtual environment and can also store other directories that are required
  - To create a pex file:
  ``` bash 
    pex [MODULES] -o [OUTPUT_FILE_NAME].pex
  ```
- Managing Spark dependencies
  - Can add spark dependencies via `spark.jars.packages
   <groupId>:<artifactId>:<version>,...`.
  - When adding multiple packages, ensure that are no spaces between package names 
  - Highly recommended to do so via `spark-submit. See [here](https://stackoverflow.com/questions/62106554/why-does-spark-submit-ignore-the-package-that-i-include-as-part-of-the-configura) and [here](https://issues.apache.org/jira/browse/SPARK-21752)`
- Kafka Advertised Listeners
  - Advertised Listeners are how clients can connect with Kafka
  - Each listener will, when connected to, report back the address at which it can be reached. 
  - The address at which you reach a broker depends on the network used. 
  - If connecting to the broker from an internal network, the host/IP will be different compared to connecting externally.
- Docker DNS:
  - Docker has a built-in DNS service which maps the IP address to aliases like, for example, the container name.
  - When the containers run, they are assigned to the same network and are assigned IP addresses.
  - Docker automatically creates a DNS record for that container, using the container name as the hostname and the IP address of the container as the record's value 
  - This enables other containers on the same network to access each other by name, rather than needing to know the IP address of the target container.
