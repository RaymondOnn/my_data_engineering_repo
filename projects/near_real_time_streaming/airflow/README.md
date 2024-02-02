### How to use?
#### Running as airflow cluster
- i.e. different components of airflow run in separate docker containers
- Use `docker-compose.yaml`
    ``` commandline
    # docker searches for docker-compose.yaml by default
    docker compose up -d 
    ```
- Note: the scheduler is critical to airflow's operations.
  - For robustness, launch multiple instances of airflow scheduler in case of failure


#### Running in standalone mode
- For running in standalone mode, use `standalone.docker-compose.yaml`
    ``` commandline
      docker compose -f standalone.docker-compose.yaml up -d 
    ```

>##### What is standalone mode?
>- Launching in `standalone mode` is done via the `airflow standalone` command.  
>- The `airflow standalone` command 
>     1. initializes the database
>     2. creates a user
>     3. starts all components.
>    ``` commandline
>    airflow db migrate
>    
>    airflow users create \
>        --username <user> \
>        --firstname <first_name> \
>        --lastname <last_name> \
>        --role <role> \
>        --email <email>
>    
>    airflow webserver --port 8080
>    
>    airflow scheduler
>    ```

