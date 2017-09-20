# this file is part of OPC-UA AddressSpace dump tool
# author: Piotr Nikiel

from pyuaf.util import Address, ExpandedNodeId, NodeId
from pyuaf.util import constants, opcuaidentifiers, nodeididentifiertypes, attributeids, nodeclasses

import pdb  #  TODO remove
import nodeset_xml
from stringify import stringify_nodeid

added_nodes = []

def get_attribute(client, expanded_node_id, attribute, context):
    result = client.read([Address(expanded_node_id)], attribute)

    if result.targets[0].status.isGood():
        
        attribute_value = result.targets[0].data.name()
        if type(attribute_value) == type(None):
            attribute_value = 'WARNING_attribute_value_is_none'
            context['errors'] += 1
    else:
        context['errors'] += 1
        browse_name = "ERROR_attribute_not_readable"
    
    return attribute_value
        

def new_context():
    return {'errors':0 }

def recurse(client, expanded_node_id, document, parent, refTypeFromParent, context):
    global added_nodes
    print 'recurse at: '+str(expanded_node_id)
    results = client.browse([Address(expanded_node_id)])
    references = results.targets[0].references  #  asked to browse only one address, that's why targets[0]

    if expanded_node_id.nodeId().nameSpaceIndex() != constants.OPCUA_NAMESPACE_ID:
        # get our browse name
        

        browse_name = get_attribute( client, expanded_node_id, attributeids.BrowseName, context)
        
        stringified_id = stringify_nodeid(expanded_node_id.nodeId() )
        if not stringified_id in added_nodes:
            result_nodeclass = client.read([Address(expanded_node_id)], attributeids.NodeClass)
            nodeclass = result_nodeclass.targets[0].data.value
            #print 'nodeclass='+str(result_nodeclass.targets[0].data)
            # wiser to go with dictionary switch (??)
            if nodeclass == nodeclasses.Object:
                # TODO : browse name fetch?
                document.append( nodeset_xml.make_element_for_uaobject( stringified_id, browse_name, references, parent, refTypeFromParent  ) )
                
            elif nodeclass == nodeclasses.Variable:
                document.append( nodeset_xml.make_element_for_uavariable( stringified_id, browse_name, references, parent, refTypeFromParent  ) )

            elif nodeclass == nodeclasses.Method:
                pass  # TODO
                
            else:
                print 'nodeclass not supported'
            added_nodes.append( stringified_id )


    for ref_i in xrange(0, len(references)):
        target = references[ref_i]
        print target
        #pdb.set_trace()
        if target.nodeId.nodeId().nameSpaceIndex() != constants.OPCUA_NAMESPACE_ID:
            recurse(client, target.nodeId, document, expanded_node_id, target.referenceTypeId, context )
        else:
            print 'Note: skipping this because both source and target are in the namespace 0 (probably coming from the UA standard). '



def main_recurse(client, server_uri, document):
    context = new_context()
    starting_address = ExpandedNodeId( opcuaidentifiers.OpcUaId_ObjectsFolder, constants.OPCUA_NAMESPACE_ID, server_uri )
    recurse(client, starting_address, document, None, None, context)
    print 'Error counter: ' + str( context['errors'] )
    
    
