# author: Piotr Nikiel
# the purpose: dump given OPC-UA address-space into a NodeSet XML file

# Don't know how to find your endpoint URL and server URI?
# endpoint URL: should be one of your OPC-UA discovery servers; or the instance URL in the last resort, which is displayed by the server when it starts up
# server URI:   is a string, often in the format urn:.... . If you use UA SDK for your servers, you can set it in the ServerConfig.xml as ApplicationUri

# this uses PyUaf: http://uaf.github.io/uaf/doc/pyuaf/

from pyuaf.client           import Client
from pyuaf.client.settings  import ClientSettings, SessionSettings
import pyuaf.client.sessionstates

import sys
import argparse

import address_space
import nodeset_xml

def connect(endpoint, server_uri):
    client_settings = ClientSettings ("pnikiel:dump", [endpoint] )
    client = Client(client_settings)
    connectionId = client.manuallyConnect(server_uri)
    sessionInfo = client.sessionInformation( connectionId )
    if sessionInfo.sessionState != pyuaf.client.sessionstates.Connected:
        raise Exception ('Couldnt connect! TODO: reason')
    print 'Connected to '+endpoint
    return (client, connectionId)

def parse_args():
    parser =  argparse.ArgumentParser(description='Dump address-space as a NodeSet')
    parser.add_argument('endpoint', type=str, help='OPC-UA endpoint, e.g. opc.tcp://127.0.0.1:4841')
    parser.add_argument('server_uri', type=str, help='OPC-UA server URI, e.g. MyCompanyName:MyServer')
    args = parser.parse_args()
    return args

def main():
    args = parse_args ()
    (client, connectionId) = connect(args.endpoint, args.server_uri)
    document = nodeset_xml.initialize_document()
    address_space.main_recurse(client, args.server_uri, document)
    
    nodeset_xml.writeout_document(document, 'output.xml')  #  TODO path cntrol


if __name__ == "__main__":
    main ()
    


