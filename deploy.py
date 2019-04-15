#!/usr/bin/python2

"""
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
"""
from docopt import docopt
from deploy_defs import *
from deploy_server import Server
from deploy_strings import *
import subprocess

def build_servers(definition):
    built_servers = []
    for server in definition['servers']:
        new_server = Server(server)
        new_server.make_mess()
        built_servers.append(new_server)
    return built_servers


def build_server(definition, hostname):
    for i, server in enumerate(definition['servers']):
        if hostname == server['hostname']:
            new_server = Server(definition['servers'][i])
            if new_server.provider == 'GCE':
                new_server.make_mess(MACHINE_CREATE_GCE)
            else:
                new_server.make_mess()

def get_server(definition, role):
    for i, server in enumerate(definition['servers']):
        if role == server['role']:
            return definition['servers'][i]


#gets server by hostname
def get_server_hostname(definition, hostname):
    for i, server in enumerate(definition['servers']):
        if hostname == server['hostname']:
            return definition['servers'][i]


def container_to_server(hostname, container):
    name = container.split("/")[1]
    server = Server(get_server_hostname(DEFINITION, hostname), env_override=name+'.env')
    server.create_env_file(env_name=name)
    server.scp_env()
    server.docker_rm(override_hostname=name)
    server.docker_login()
    server.docker_pull(container)
    if name == 'vader':
       server.docker_create(DEFINITION, name=name, override=True, container=container, env_override=True)
    else:
        server.docker_create(DEFINITION, name=name, override=True, container=container)
    server.docker_start(name)


def main():
    args = docopt(__doc__, version="deploy.py 1.0")

    if args['--deploy']:
        build_server(DEFINITION, args['<hostname>'])

    if args['--repop']:
        server = Server(get_server_hostname(DEFINITION, args['<hostname>']))
        server.replace_restart()

    if args['--deploy-container']:
        container_to_server(args['<hostname>'], args['<container>'])

    if args['--scp-env']:
        server = Server(get_server(DEFINITION, args['<hostname>']))
        server.scp_env()

    if args['--docker-start']:
        server = Server(get_server(DEFINITION, args['<hostname>']))
        server.docker_start()

    if args['--docker-create']:
        server = Server(get_server(DEFINITION, args['<hostname>']))
        server.docker_rm()
        server.docker_create(DEFINITION, args['<hostname>'])

    if args['--docker-pull']:
        server = Server(get_server(DEFINITION, args['<hostname>']))
        server.docker_pull()

    if args['--remove']:
        server = Server(get_server_hostname(DEFINITION, args['<hostname>']))
        server.destory_server()

if __name__ == '__main__':
    main()