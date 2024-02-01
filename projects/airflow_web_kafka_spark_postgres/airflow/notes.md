
Deploy notes:
- Except for simple commands, avoid running it in Airflow
  - try to trigger the workflow instead i.e. SSH, Rest APIs, Kubernetes, SparkSubmitOperator
  - Communication between docker containers can be done via SSH
- Managing dependencies can be done via containers i.e. Docker, Kubernetes
- Dynamically create DAGs
  - Essential if were to provide Airflow as a service
  - Generally two methods
    - Create DAG objects 
      - Possible issues with memory and debugging but everyone seems to use this with no issues
    - Create DAG files that create DAG object
- Configuring concurrency (i.e. Pools)
  - seems to help with deployment at scale

To-Dos:
- [ ] Set Up Working Airflow Dag
- [ ] Airflow Dynamic Dags
- [ ] Airflow Pools
- [ ] Airflow Practices In Production
- [ ] ClusterPack for Spark Packaging
- [ ] Test DAG