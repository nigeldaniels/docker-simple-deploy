# docker-simple-deploy
Docker simple-deploy was a wrapper for docker-machine as well as RDS for deploying small scale dockerized services. 

It supported the fallowing features 
```
Usage:
    deploy.py [options]
    deploy.py --docker-login <hostname>
    deploy.py --deploy-container <container> <hostname>
    deploy.py --scp-env <hostname>
    deploy.py --docker-create <hostname>
    deploy.py --mkdir <hostname>
    deploy.py --docker-start <hostname>
    deploy.py --docker-pull <hostname>
    deploy.py --deploy <hostname>
    deploy.py --docker-build <role>
    deploy.py --test-vault <role>
    deploy.py --remove <hostname>
    deploy.py --repop <hostname>

Options:
    --deploy-all        deploys all servers
    --docker-login      docker logs into dockerhub
    --scp-env           sends env file over ssh to the specified host
    --docker-create     runs docker create on the specified host
    --create-database   creates the rds defined in deploy_defs.py
    --mkdir             makes /docker-share directory
    --docker-start      starts the docker container defined in defs on the specified host
    --docker-pull       pulls the defined container from dockerhub
    --deploy            builds the specified server does not add docker containers
    --docker-build      builds the container specified by <role>
    --remove            deletes server from cloud, sensu and opensips db
    --repop             this redeploys a container to an exsisting server
    --deploy-container  deploys a container of the specified name to the host
    ````
