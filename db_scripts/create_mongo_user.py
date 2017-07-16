from pymongo import MongoClient

import traceback
import sys
import json
import argparse
import requests
from requests.api import request
try:
    # For Python 3.0 and later
    from urllib.request import urlopen
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen



def getIpPortDns(mesosDnsAddr, serviceMesosDns):
    
    '''
        [
        {
        "service": "_auth-db-auth._tcp.marathon.mesos.",
        "ip": "10.0.0.13",
        "port": "31332"
        }
        ]
        '''
    
    response = requests.get(mesosDnsAddr + "/v1/services/" + serviceMesosDns, timeout = 20)
    if response.status_code == requests.codes.ok:
        #print(response.text)
        responseJson = json.loads(response.text)
        ip = responseJson[0]["ip"]
        port = responseJson[0]["port"]
        if not ip:
            print("No ip for " + serviceMesosDns)
        if not port:
            print("No port for " + serviceMesosDns)
    else:
        print("Error getting ip/port for " + serviceMesosDns)
        ip = ""
        port = ""
    return (ip, port)


_CODE_CREATE_USER = """
    db.getSiblingDB('$external').runCommand(
    {
    createUser: 'OU=mongo_client,O=Bigsea,L=Campinas,ST=SP,C=BR',
    roles: [
    { role: 'readWrite', db: 'AAADB' },
    { role: 'read', db: 'AAADB' }
    ],
    writeConcern: { w: 'majority' , wtimeout: 5000 }
    }
    )
    """


_DEFAULT_DB_HOST = '10.0.0.7'
_DEFAULT_DB_PORT = 44802
_DEFAULT_DB_NAME = 'AAADB'
_DEFAULT_CLIENT_CERT = 'certs/mongo_client_crt.pem'
_DEFAULT_CA_CERT = 'certs/root_ca.pem'
_DEFAULT_USER = 'OU=mongo_client,O=Bigsea,L=Campinas,ST=SP,C=BR'
_DEFAULT_MECHANISM = 'MONGODB-X509'

if __name__ == '__main__':
    
    print("Running the Mesos DNS ip/port extractor")
    parser = argparse.ArgumentParser(description="Get the ip/port for various services from Mesos DNS")
    parser.add_argument('--mesosdns', required=True, help='Mesos DNS full address e.g. http://127.0.0.1:8123')
    parser.add_argument('--mesosdns_db', required=True, help="Mesos DNS full name for the DB e.g. '_auth-db-auth._tcp.marathon.mesos.'")
    parser.add_argument('--vars', required=True, help="The full path of the file which will be generated by this script. It will contain the new values for various env variables that are needed by the web-app e.g. './vars.rc'")
    
    args = parser.parse_args()
    varsFName = args.vars
    mesosDnsAddr = args.mesosdns
    mesosDnsDb = args.mesosdns_db
    
    
    with open(varsFName, "w") as varsF:
        ipPort = getIpPortDns(mesosDnsAddr, mesosDnsDb)
        print("AUTH_DB_HOST IP: " + ipPort[0])
        print("AUTH_DB_HOST PORT: " + ipPort[1])
        varsF.write("AUTH_DB_HOST=" + ipPort[0] + "\n")
        varsF.write("AUTH_DB_PORT=" + ipPort[1] + "\n")
    
    
    client = MongoClient(_DEFAULT_DB_HOST, _DEFAULT_DB_PORT)
    
    '''client = MongoClient(ipPort[0], ipPort[1])'''
    db = client["admin"]
    db.add_user("admin", pwd="tijolo22",
                roles=[{'role':'readWrite', 'db':'AAADB'},
                       {'role':'userAdminAnyDatabase', 'db': 'admin'}])
    db.authenticate("admin", "tijolo22")
    db.eval(_CODE_CREATE_USER)

