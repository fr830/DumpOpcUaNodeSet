# this file is part of OPC-UA AddressSpace dump tool
# author: Piotr Nikiel

from pyuaf.util import Address, ExpandedNodeId
from pyuaf.util import constants, opcuaidentifiers, nodeididentifiertypes

import pdb  #  TODO remove
import nodeset_xml

def stringify_nodeid( nodeid ):
    if nodeid.identifier().type == nodeididentifiertypes.Identifier_String:
        return "ns=" + str(nodeid.nameSpaceIndex()) + ";s=" + nodeid.identifier().idString
    elif nodeid.identifier().type == nodeididentifiertypes.Identifier_Numeric:
        return "ns=" + str(nodeid.nameSpaceIndex()) + ";i=" + str(nodeid.identifier().idNumeric)
    else:
        return "not-supported"

def recurse(client, address, document):
    print 'recurse: '+str(address)
    results = client.browse([address])
    references = results.targets[0].references  #  asked to browse only one address, that's why targets[0]
    for ref_i in xrange(0, len(references)):
        target = references[ref_i]
        #  if source and target are both in UA nodespace, skip them.
        #  TODO: make it optional
        # pdb.set_trace()
        if address.getExpandedNodeId().nodeId().nameSpaceIndex() != constants.OPCUA_NAMESPACE_ID and target.nodeId.nodeId().nameSpaceIndex() != constants.OPCUA_NAMESPACE_ID:
            document.append( nodeset_xml.make_element_for_uaobject( stringify_nodeid( target.nodeId.nodeId() ) ) )
            recurse(client, Address(target.nodeId), document )
        else:
            print 'Note: skipping this because both source and target are in the namespace 0 (probably coming from the UA standard). '



def main_recurse(client, server_uri, document):
    starting_address = Address( ExpandedNodeId( opcuaidentifiers.OpcUaId_ObjectsFolder, constants.OPCUA_NAMESPACE_ID, server_uri ) )  
    recurse(client, starting_address, document)
    
    
