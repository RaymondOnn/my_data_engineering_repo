# Generate pex file via docker image 

### Building the docker image
- When building the docker image, you will need to supply the python version (3.XX) you want 
- `$PYTHON_VERSION`defaults to `3.10`
- To build image:
``` commandline
docker build --build-arg <PYTHON_VERSION> -t <IMG_NAME> <WORKDIR>
```
### Generating the pex file
```commandline
docker run --rm -v $(pwd):/build <IMG_NAME> <PEX_COMMAND>
```
    
- An example of pex command:

    ``` commandline
    [COMMAND]: pex ansible==2.3.0.0 -c ansible-playbook -o ansible-playbook
    ```
