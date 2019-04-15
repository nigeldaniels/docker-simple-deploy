import sys
import subprocess
from deploy_strings import *
from deploy_defs import *
from requests_toolbelt.adapters import host_header_ssl
sys.path.append('..')
import dockerized.base.data.dns as dns
import os
import hvac
import string
import random
import redis
import requests
import time
from db_psycopg2 import db

opensipsdb = os.environ['OS_DB_URL']
RULE = 'rule'

class Server(object):
    def __init__(self, server_def, env_override=None):
        self.container = server_def.get('container', '')
        self.region = server_def.get('region', 'dal01')
        self.cpus = server_def.get('cpus', '4')
        self.memory = server_def.get('memory', '2048')
        self.disk = server_def.get('disk', '25')
        self.address = server_def.get('address', None)
        self.ports = server_def.get('ports', None)
        self.provider = server_def.get('provider', 'softlayer')
        self.hostname = server_def['hostname']
        self.domain = server_def['domain']
        self.softlayer_api = os.environ['SL_API']
        self.softlayer_username = os.environ['SL_USER']
        self.container = server_def['container']
        self.role = server_def['role']
        self.iptables_rules = "NORULES!"
        self.zone = server_def.get('zone')
        self.ENV_FILE = self.hostname+'.env'

        if self.provider == 'GCE':
            self.DOCKER_MACHINE_SSH = DOCKER_MACHINE_SSH_sudo.format(self.hostname)
        else:
            self.DOCKER_MACHINE_SSH = DOCKER_MACHINE_SSH.format(self.hostname)

        if env_override:
            self.DOCKER_MACHINE_SCP = DOCKER_MACHINE_SCP.format(env_override, self.hostname, env_override)
        else:
            self.DOCKER_MACHINE_SCP = DOCKER_MACHINE_SCP.format(self.ENV_FILE, self.hostname, self.ENV_FILE)

        self.MACHINE_PATH = MACHINE_PATH.format(self.hostname, self.hostname+'.env')
        self.extra_ops = ''
        self.vault_client = self.vault_auth()

    def forward_ports(self):
        if self.ports is not None:
            for i, port in enumerate(self.ports):
                print "forwarding %", port
                command = GCLOUD_FORWARD.format(self.zone, RULE+str(i), "UDP", port, self.hostname)
                subprocess.call(command, shell=True)
                command = GCLOUD_FORWARD.format(self.zone, RULE+"-tcp"+str(i), "TCP", port, self.hostname)
                subprocess.call(command, shell=True)
        else:
            print "no ports to forward"

    def deploy_container(self, role=None, container=None, name=None):
        self.container = container
        self.role = role
        self.create_env_file()
        self.docker_build()
        self.docker_pull()
        if role is not None:
            self.docker_create(DEFINITION, name=name)
        else:
            self.docker_create(None, name=name)
        self.scp_env()
        self.docker_start(name=name)

    def make_mess(self, alt_machine=None):
        self.role_specifc_env()
        self.create_env_file()
        self.create_server(alt_machine)
        self.forward_ports()
        self.docker_rm()
        self.docker_login()
        self.docker_pull()
        self.docker_mkdir()
        self.scp_env()
        self.docker_create(DEFINITION)
        self.docker_start()
        self.role_specific()

    def replace_restart(self):
        self.docker_rm()
        self.deploy_container(self.role, self.container, name=self.hostname)

    def role_specific(self):
        print "ROLE:", self.role
        if self.role == "opensips":
            dns.simple_create(self.domain, self.get_ip())
            dns.simple_create('echelonfs.sip.talkiq.net', self.get_ip())
            dns.simple_create('aspfs.sip.talkiq.net', self.get_ip())

        if self.role == "redswitch":
            self.deploy_container("redswitch", "talkiq/redswitch", name="redswitch")

        if self.role == "realtime":
            dns.simple_create(self.hostname+'.'+self.domain, self.get_ip())

        if self.role == "echelonfs":
            self.deploy_container("vader", "talkiq/vader", name="vader")

        if self.role =="aspfs":
            self.deploy_container("plivo", "talkiq/plivo", name="plivo")

    def role_specifc_env(self):
        if self.role == "echelonfs":
            self.iptables_rules = "janus.rules"

        if self.role == "aspfs":
            self.iptables_rules = "sniff.rules"

        else:
            self.iptables_rules = "norules"

    def pw_gen(self, size=16, chars=string.ascii_letters + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))

    def create_env_file(self, env_name=None):

        AWS_ACCESS_KEY_ID = self.vault_client.read(GLOBAL_SECRET.format('AWS_ACCESS_KEY_ID'))['data']['key']
        AWS_SECRET_ACCESS_KEY = self.vault_client.read(GLOBAL_SECRET.format('AWS_SECRET_ACCESS_KEY'))['data']['key']
        LOGGLY_AUTH_TOKEN = self.vault_client.read(GLOBAL_SECRET.format('LOGGLY_AUTH_TOKEN'))['data']['key']
        GITHUB_OAUTH = self.vault_client.read(GLOBAL_SECRET.format('GITHUB_OAUTH'))['data']['key']
        DATABASE_HOST = self.vault_client.read(GLOBAL_SECRET.format('DATABASE_HOST'))['data']['key']
        REDIS_URL = self.vault_client.read(GLOBAL_SECRET.format('REDIS_URL'))['data']['key']
        OS_DB_URL = self.vault_client.read(GLOBAL_SECRET.format('OS_DB_URL'))['data']['key']
        OPENSIPS_JSON_PASSWORD = self.vault_client.read(GLOBAL_SECRET.format('OPENSIPS_JSON_PASSWORD'))['data']['key']
        DATABASE_USER = self.vault_client.read(GLOBAL_SECRET.format('DATABASE_USER'))['data']['key']
        DATABASE_PASSWORD = self.vault_client.read(GLOBAL_SECRET.format('DATABASE_PASSWORD'))['data']['key']
        GOOGLE_SERVICE_ASR = self.vault_client.read(GLOBAL_SECRET.format('GOOGLE_SERVICE_ASR'))['data']['key']
        FLOWROUTE_PREFIX = self.vault_client.read(GLOBAL_SECRET.format('FLOWROUTE_PREFIX'))['data']['key']
        PUBSUB_REDIS_URL = self.vault_client.read(GLOBAL_SECRET.format('PUBSUB_REDIS_URL'))['data']['value']

        if env_name is None:
            env_name = self.hostname

        with open(env_name + '.env', 'w') as f:
            if env_name == 'vader':
                f.write("SENSU_CLIENT_NAME=" + self.hostname + '-vader' + '\n')

            f.write("DOMAIN=" + self.domain + '\n')
            f.write("AWS_SECRET_ACCESS_KEY=" + AWS_SECRET_ACCESS_KEY + '\n')
            f.write("AWS_ACCESS_KEY_ID=" + AWS_ACCESS_KEY_ID + '\n')
            f.write("LOGGLY_AUTH_TOKEN=" + LOGGLY_AUTH_TOKEN + '\n')
            f.write("GITHUB_OAUTH=" + GITHUB_OAUTH + '\n')
            f.write("DATABASE_HOST=" + DATABASE_HOST + '\n')
            f.write("REDIS_URL=" + REDIS_URL + '\n')
            f.write("OS_DB_URL=" + OS_DB_URL + '\n')
            f.write("OPENSIPS_JSON_PASSWORD=" + OPENSIPS_JSON_PASSWORD + '\n')
            f.write("DATABASE_PASSWORD=" + DATABASE_PASSWORD + '\n')
            f.write("DATABASE_USER=" + DATABASE_USER + '\n')
            f.write("AUTH_USERNAME=" + self.hostname + '\n')
            f.write("AUTH_PASSWORD=" + self.pw_gen() + '\n')
            f.write("DOMAIN=" + self.domain + '\n')
            f.write("GOOGLE_SERVICE_ASR=" + GOOGLE_SERVICE_ASR + '\n')
            f.write("BRIDGE_CACHE_INTERVAL=60" + '\n')
            f.write("FLOWROUTE_PREFIX=" + FLOWROUTE_PREFIX + '\n')
            f.write("HOSTNAME=" + self.hostname + '\n')
            f.write("JANUS_INTERFACE=flannel.1\n")
            f.write("JANUS_GS_SIP_BUCKET=talkiq-echelon-sip\n")
            f.write("JANUS_GS_RTP_BUCKET=talkiq-echelon-streams\n")
            f.write("JANUS_USER_KIND=User\n")
            f.write("DATASTORE_TABLE=stream\n")
            f.write("PROJECT=talkiq-echelon\n")
            f.write("JANUS_ORG_KIND=Organization\n")
            f.write("JANUS_USER_KIND=User\n")
            f.write("JANUS_GS_SIP_BUCKET=talkiq-echelon-sip\n")
            f.write("JANUS_GS_RTP_BUCKET=talkiq-echelon-streams\n")
            f.write("STREAM_API_URL=http://oauth.talkiq.com/oauth/stream\n")
            f.write("URLSAFE_API_URL=http://oauth.talkiq.com/oauth/keymaster/list\n")
            f.write("SNIFF_DATASTORE_KIND=stream\n")
            f.write("SNIFF_GCLOUD_PROJECT=talkiq-echelon\n")
            f.write("SNIFF_RTP_BUCKET=talkiq-echelon-streams\n")
            f.write("SNIFF_SIP_BUCKET=talkiq-echelon-sip\n")
            f.write("redis://redis:tloirydvagdyoowrickigpiityktois@104.196.238.30:6379\n")
            f.write("PUBSUB_REDIS_URL="+PUBSUB_REDIS_URL+"\n")
            f.write("IPTABLES_RULES="+self.iptables_rules+"\n")
            f.write("DOCKER_SHARE_DIR=/"+"\n")
            f.write("REALTIME_CALLEE_HOST=rtcallee.talkiq.net\n")
            f.write("REALTIME_CALLER_HOST=rtcaller.talkiq.net\n")
            f.write("REALTIME_CALLEE_PORT=10011\n")
            f.write("REALTIME_CALLER_PORT=10011\n")
            f.write("ESL_URL=127.0.0.1\n")
            f.write("ESL_PORT=8021\n")
          #  f.write("IP_ADDRESS=" + self.ip + "\n")
            f.write("ESL_PASSWORD=ClueCon\n")
            f.write("DEST_GATEWAY=sofia/gateway/opensips/\n")
            f.write("REDIS_URL={}\n".format(os.environ['REDIS_URL']))

    def __reduce__(self, *args, **kwargs):
        return super(Server, self).__reduce__(*args, **kwargs)

    def create_server(self, alt_machine=None):
        if alt_machine is not None:
            command = MACHINE_CREATE_GCE.format(self.address, self.hostname)
        else:
            command = MACHINE_CREATE.format(self.softlayer_username,
                                            self.softlayer_api,
                                            self.domain,
                                            self.cpus,
                                            self.hostname,
                                            self.memory, self.disk, self.region, self.hostname)
        subprocess.call(command, shell=True)
        if alt_machine is not None:
            command = TARGET_INSTANCE_CREATE.format(self.hostname, self.zone, self.zone, self.hostname)
            subprocess.call(command, shell=True)

    def docker_local_login(self):
        command = DOCKER_LOGIN.format(REGISTRY_USER, REGISTRY_PASSWORD)
        subprocess.call(command, shell=True)

    def docker_local_push(self):
        print self.container
        command = DOCKER_PUSH.format(self.container)
        subprocess.call(command, shell=True)

    def docker_build(self, override_role=False):
        if override_role:
            self.docker_local_login()
            command = DOCKER_BUILD.format(DK_PATH, override_role)
            subprocess.call(command, shell=True)
            self.docker_local_push()
        else:
            self.docker_local_login()
            command = DOCKER_BUILD.format(DK_PATH, self.role)
            subprocess.call(command, shell=True)
            self.docker_local_login()
            self.docker_local_push()

    def docker_rm(self, override_hostname=False):
        if override_hostname:
            command = self.DOCKER_MACHINE_SSH + ' docker rm -f ' + override_hostname
        else:
            command = self.DOCKER_MACHINE_SSH + ' docker rm -f ' + self.hostname
        print command
        subprocess.call(command, shell=True)

    def scp_env(self):
        command = self.DOCKER_MACHINE_SCP
        print command
        subprocess.check_output(command, shell=True)
        subprocess.check_output('rm -rf ' + self.hostname+'.env', shell=True)

    def docker_pull(self, container_override=False):
        if container_override:
            command = self.DOCKER_MACHINE_SSH + DOCKER_PULL.format(container_override)
        else:
            command = self.DOCKER_MACHINE_SSH + DOCKER_PULL.format(self.container)
        subprocess.check_output(command, shell=True)

    def docker_login(self):
        command = self.DOCKER_MACHINE_SSH + DOCKER_LOGIN.format(REGISTRY_USER, REGISTRY_PASSWORD)
        subprocess.check_output(command, shell=True)

    def docker_mkdir(self):
        command = self.DOCKER_MACHINE_SSH + ' mkdir -p /docker-share'
        subprocess.check_output(command, shell=True)

    def docker_create(self, definition, host='', name=None, override=False, container=None, env_override=None):
        if override is True:
            command = self.DOCKER_MACHINE_SSH + DOCKER_CREATE_SIMPLE.format(name, self.hostname, container)
        if env_override:
            command = self.DOCKER_MACHINE_SSH + DOCKER_CREATE_SIMPLE.format(name, name, container)
        else:
            self.check_def(definition, host=host)
            if name is not None:
                if self.role == 'logstash':
                    rm_command = self.DOCKER_MACHINE_SSH + DOCKER_RM.format(name)
                    command = self.DOCKER_MACHINE_SSH + DOCKER_CREATE_SIMPLE.format(name, self.hostname, self.container)
                else:
                    rm_command = self.DOCKER_MACHINE_SSH + DOCKER_RM.format(name)
                    command = self.DOCKER_MACHINE_SSH + DOCKER_CREATE_SIMPLE.format(name, self.hostname, self.container)
            else:
                rm_command = self.DOCKER_MACHINE_SSH + DOCKER_RM.format(self.hostname)
                command = self.DOCKER_MACHINE_SSH + DOCKER_CREATE_SIMPLE.format(self.hostname, self.hostname, self.container)

            print rm_command
            subprocess.call(rm_command, shell=True)
            print command
        subprocess.check_output(command, shell=True)

    def check_def(self, definition, host):
        if self.container =='':
            for server in definition['servers']:
                if host == server['hostname']:
                    self.container = server['container']

    def docker_start(self, name=None):
        if name is not None:
            command = self.DOCKER_MACHINE_SSH + ' docker start ' + name
        else:
            command = self.DOCKER_MACHINE_SSH +' docker start ' + self.hostname
        subprocess.check_output(command, shell=True)

    def get_ip(self):
        command = DOCKER_MACHINE_IP.format(self.hostname)
        return subprocess.check_output(command, shell=True)

    def destory_server(self):
        command = DOCKER_MACHINE_RM.format(self.hostname)
        self.reload_opensips()
        self.remove_db_record()
        print "press y to confirm remove" + '\n'
        subprocess.check_output(command, shell=True)
        self.remove_from_sensu()

    def remove_db_record(self):
        db.from_url(opensipsdb)
        try:
            db.do("""DELETE FROM subscriber where username = %X""", self.hostname)
        except Exception:
            print "The Deleted host was not removed from the subscriber table"
        try:
            db.do("""DELETE FROM load_balancer where dst_uri LIKE %X  """, '%X'+self.hostname+'%X')
        except Exception:
            print "the Deleted host was not removed from the load_balancer table"

    def remove_from_sensu(self):
        try:
            name = self.hostname
            redis_url = os.environ['REDIS_URL']
            r = redis.StrictRedis.from_url(redis_url, db=0)
            keys = r.keys('*{}*'.format(name))
            r.delete(*keys)
        except Exception as e:
            print "The host was not removed from sensu"

    def reload_opensips(self):
        http_auth = ('freeswitch', self.vault_client.read(GLOBAL_SECRET.format('OPENSIPS_JSON_PASSWORD'))['data']['key'])
        requests.get('http://sip.talkiq.net:8001/opensips_mi_json/domain_reload', auth=http_auth)
        requests.get('http://sip.talkiq.net:8001/opensips_mi_json/domain_reload', auth=http_auth)

    def vault_auth(self):
        vault_client = hvac.Client(url=os.environ['VAULT_ADDR'], token=os.environ['VAULT_TOKEN'])
        vault_client.session.mount('https://', host_header_ssl.HostHeaderSSLAdapter())
        vault_client.session.headers['Host'] = VAULT_TLS_SERVER_NAME
        token = vault_client.auth_approle(vault_client.read(ROLE_ID_PATH)['data']['role_id'], vault_client.write(SECRET_ID_PATH)['data']['secret_id'])['auth']['client_token']
        vault_client.token = token
        return vault_client
