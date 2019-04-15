import os
MACHINE_CREATE_GCE = """
docker-machine create --driver google \
--google-project talkiq-echelon \
--google-zone us-central1-a \
--google-machine-image https://www.googleapis.com/compute/v1/projects/ubuntu-os-cloud/global/images/family/ubuntu-1604-lts \
--google-machine-type n1-standard-1 \
--google-address {} \
{}


"""
MACHINE_CREATE="""
docker-machine create \
--driver softlayer \
--softlayer-user={} \
--softlayer-api-key={} \
--softlayer-domain={} \
--softlayer-cpu={} \
--softlayer-hostname={} \
--softlayer-memory={} \
--softlayer-disk-size={} \
--softlayer-region={} \
--softlayer-hourly-billing=true \
--softlayer-image=UBUNTU_LATEST \
{} \
"""
#rulename, proto, port, instance

GCLOUD_FORWARD = """
CLOUDSDK_COMPUTE_ZONE={} gcloud compute forwarding-rules create {} --region us-central1 --ip-protocol {} \
    --ports {} --target-instance {} \
"""

DOCKER_CREATE = """docker create --name {} \
--privileged \
--net=host \
--env-file {}.env \
{}:latest \
"""

DOCKER_CREATE_SIMPLE = """docker create --name {} \
--privileged \
--net=host \
--env-file {}.env \
{}:latest \
"""

DOCKER_RM = "docker rm -f {}"
DK_PATH = '~/code/infrastructure/bin/dk-prod'

DOCKER_BUILD="""
{} build {} \
"""

GLOBAL_SECRET = """secret/global/{}"""
SECRET_PATH = """secret/{}"""
ROLE_ID_PATH = 'auth/approle/role/app/role-id'
SECRET_ID_PATH = 'auth/approle/role/app/secret-id'
VAULT_ADDR = os.environ['VAULT_ADDR']
VAULT_TOKEN = os.environ['VAULT_TOKEN']
REGISTRY_USER = os.environ['DOCKER_USER']
REGISTRY_PASSWORD = os.environ['DOCKER_PASSWORD']
SSH = ' ssh '
SCP = ' scp '
AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
DOCKER_MACHINE = 'docker-machine'
DOCKER_MACHINE_IP = 'docker-machine ip {}'
DOCKER_MACHINE_SSH = 'docker-machine ssh {} '
DOCKER_MACHINE_SSH_sudo = 'docker-machine ssh  {} sudo '
DOCKER_MACHINE_SCP = 'docker-machine scp {} {}:{}'
DOCKER_MACHINE_RM = 'docker-machine rm {}'
DOCKER_PULL = 'docker pull {}'
DOCKER_PUSH = 'docker push {}'
DOCKER_LOGIN = 'docker login -u {} -p {}'
manager_token = ' docker swarm join-token -q {}'
FIRST_MANAGER = 'opensips' #this may need to be stored later .docker/machine/machines/opensips/
DOCKER_REMOTE_API_PORT = ':2376'
MACHINE_PATH = '~/.docker/machine/machines/{}/{}' #hostname,file
ENV_FILE = '/etc/talkiq.env'
VAULT_ADDR = 'https://vault.talkiq.net:8200'
VAULT_TLS_SERVER_NAME = 'vault.talkiq.net'
TARGET_INSTANCE_CREATE="gcloud compute target-instances create {} --zone {} --instance-zone {} --instance {}"
