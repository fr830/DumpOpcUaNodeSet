# this file is part of OPC-UA AddressSpace dump tool
# author: Piotr Nikiel

from pyuaf.util import Address, ExpandedNodeId, NodeId
from pyuaf.util import constants, opcuaidentifiers, nodeididentifiertypes, attributeids

import pdb  #  TODO remove
import nodeset_xml
from stringify import stringify_nodeid

added_nodes = []

def recurse(client, expanded_node_id, document, parent, refTypeFromParent):
    global added_nodes
    print 'recurse at: '+str(expanded_node_id)
    results = client.browse([Address(expanded_node_id)])
    references = results.targets[0].references  #  asked to browse only one address, that's why targets[0]

    if expanded_node_id.nodeId().nameSpaceIndex() != constants.OPCUA_NAMESPACE_ID:
        # get our browse name
        result = client.read([Address(expanded_node_id)], attributeids.BrowseName)

        if result.targets[0].status.isGood():
            browse_name = result.targets[0].data.name()
        else:
            browse_name = "*BROWSE_NAME_FAIL*"
    
        
        stringified_id = stringify_nodeid(expanded_node_id.nodeId() )
        if not stringified_id in added_nodes:
            document.append( nodeset_xml.make_element_for_uaobject( stringified_id, browse_name, references, parent, refTypeFromParent  ) )
            added_nodes.append( stringified_id )


    for ref_i in xrange(0, len(references)):
        target = references[ref_i]
        print target
        #pdb.set_trace()
        if target.nodeId.nodeId().nameSpaceIndex() != constants.OPCUA_NAMESPACE_ID:
            recurse(client, target.nodeId, document, expanded_node_id, target.referenceTypeId )
        else:
            print 'Note: skipping this because both source and target are in the namespace 0 (probably coming from the UA standard). '



def main_recurse(client, server_uri, document):
    starting_address = ExpandedNodeId( opcuaidentifiers.OpcUaId_ObjectsFolder, constants.OPCUA_NAMESPACE_ID, server_uri )
    recurse(client, starting_address, document, None, None)
    
    
