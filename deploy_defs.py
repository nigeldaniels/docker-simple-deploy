"""
Server deffinitions

"""



DEFINITION = {

        "servers":[
            {
                "hostname": "opensips",
                "role": "opensips",
                "domain": "sip.talkiq.net",
                "container": "talkiq/opensips",
                "cpus": "2",
                "disk": "100",
                "memory": "16384",
                "region": "dal01"
            },

            {
                "hostname": "efs5",
                "role": "echelonfs",
                "domain": "redacted.sip.redacted.net",
                "container": "redacted_registry/echelonfs",
                "cpus": "2",
                "disk": "100",
                "memory": "16384",
                "region": "sjc01"
            },


            {
                "hostname": "efs4",
                "role": "echelonfs",
                "domain": "redacted.sip.redacted.net",
                "container": "redacted_registry/echelonfs",
                "cpus": "2",
                "disk": "100",
                "memory": "16384",
                "region": "dal01"
            },

            {
                "hostname": "dp1",
                "role": "dialpad",
                "domain": "redacted.sip.redacted.net",
                "container": "redacted_registry/echelonfs",
                "cpus": "2",
                "disk": "100",
                "memory": "16384",
                "region": "sjc01"
            },

            {
                "hostname": "dp2",
                "role": "dialpad",
                "domain": "redacted.sip.redacted.net",
                "container": "redacted_registry/echelonfs",
                "cpus": "2",
                "disk": "100",
                "memory": "16384",
                "region": "sjc01"
            },

            {
                "hostname": "loadtest2",
                "role": "dialpad",
                "domain": "redacted.sip.redacted.net",
                "container": "redacted_registry/echelonfs",
                "cpus": "4",
                "disk": "100",
                "memory": "32768",
                "region": "dal01",
            },

            {
                "hostname": "loadtest3",
                "role": "dialpad",
                "domain": "redacted.sip.redacted.net",
                "container": "redacted_registry/echelonfs",
                "cpus": "8",
                "disk": "100",
                "memory": "32768",
                "region": "dal01",
            },

            {
                "hostname": "vadertest",
                "role": "echelonfs",
                "domain": "redacted.sip.redacted.net",
                "container": "redacted_registry/echelonfs",
                "cpus": "2",
                "disk": "100",
                "memory": "16384",
                "region": "dal01"
            },


            {
                "hostname": "flanneltest",
                "role": "echelonfs",
                "domain": "redacted.sip.redacted.net",
                "container": "redacted_registry/echelonfs",
                "cpus": "2",
                "disk": "100",
                "memory": "16384",
                "region": "sjc01"
            },


            {
                "hostname": "efs3",
                "role": "echelonfs",
                "domain": "echelonfs.sip.talkiq.net",
                "container": "talkiq/echelonfs",
                "cpus": "2",
                "disk": "100",
                "memory": "16384",
                "region": "dal01"

            },

            {
                "hostname": "aspfs",
                "role": "aspfs",
                "domain": "redacted.sip.redacted.net",
                "cpus": "2",
                "disk": "100",
                "container": "redacted/echelonfs",
                "memory": "16384",
                "region": "sjc01",

            },

            {
                "hostname": "aspfs2",
                "role": "aspfs",
                "domain": "redacted.sip.redacted.net",
                "cpus": "2",
                "disk": "100",
                "container": "redacted/echelonfs",
                "memory": "16384",
                "region": "sjc01",

            },

            {
                "hostname": "sniffdp",
                "role": "sniff",
                "domain": "redacted.net",
                "cpus": "2",
                "disk": "100",
                "container": "redacted/echelonfs",
                "memory": "16384",
                "region": "sjc01",

            },


            {
                "hostname": "newlogstash",
                "role": "logstash",
                "domain": "redacted.net",
                "container": "redacted/logstash",
                "cpus": "2",
                "disk": "100",
                "memory": "16384",
                "region": "sjc01"
            },


        ],

        }
