# pyspark-template
A template with PEX for running PySpark Jobs 

#### Setting Things Up
- Add your files in a folder under `app/jobs/<JOB_NAME>`
    - Name the folder accordingly. 
    - Note: Jobs are selected for execution based on this name

``` MD
spark-submit template
 ├── app
 │    │── jobs
 │    │    ├──<JOB_NAME>
 │    │    │    ├── requirements.txt
 │    │    │    ├── config.yaml
 │    │    │    ├── __init__.py
 │    │    │    ├── main.py
 │    │    └── entrypoint.py
 │    │── dist
 │    │── logs   
 │    └── tests
 ├── conf                       # spark-defaults.conf stored here...
 ├── docker-compose.yaml
 ├── Makefile
 └── README.md
```
- Update Makefile variables
  - Update the `JOB_NAME` variable
  - Check the `spark-submit` command
    - for `spark.jars.packages`, please do it via the `spark-submit` command

#### The Spark Cluster in Docker Containers
- To start Spark cluster:
    ```makefile
    # Runs spark in standalone mode
    make start-spark
    ```
- To stop Spark cluster:
    ```makefile
    make stop-spark
   ``` 
#### Executing Pyspark Job
Currently, pex is used for managing python dependencies
1. To create a pex file for your job:
    ``` makefile 
    make pex
    ```
2. Next, to `spark-submit` your job:
    ``` makefile 
    make submit
    ```