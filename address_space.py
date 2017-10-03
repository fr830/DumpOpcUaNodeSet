# this file is part of OPC-UA AddressSpace dump tool
# author: Piotr Nikiel

from pyuaf.util import Address, ExpandedNodeId, NodeId, LocalizedText, QualifiedName
from pyuaf.util import constants, opcuaidentifiers, nodeididentifiertypes, attributeids, nodeclasses, primitives

import pdb  #  TODO remove
import nodeset_xml
from stringify import stringify_nodeid

added_nodes = []

def get_attribute(client, expanded_node_id, attribute, context):
    result = client.read([Address(expanded_node_id)], attribute)
    
    if result.targets[0].status.isGood():
        data = result.targets[0].data
        if type(data) == LocalizedText:
            attribute_value = data.text()
        elif type(data) in [primitives.Int32, primitives.Byte, primitives.Boolean]:
            attribute_value = data.value
        elif type(data) == QualifiedName:
            attribute_value = data.name()
        elif type(data) == NodeId:
            attribute_value = stringify_nodeid( data )
        elif type(data) == type(None):
            attribute_value = 'WARNING_attribute_value_is_none'
            context['errors'] += 1
        else:
            raise Exception("Don't know what to do when typs is {0}".format(str(type(data))))
    else:
        context['errors'] += 1
        attribute_value = "ERROR_attribute_not_readable"
    
    return attribute_value
        

def new_context():
    return {'errors':0 }

def recurse(client, expanded_node_id, document, parent, refTypeFromParent, context):
    global added_nodes
    print 'recurse at: '+str(expanded_node_id)
    results = client.browse([Address(expanded_node_id)])
    references = results.targets[0].references  #  asked to browse only one address, that's why targets[0]

    if expanded_node_id.nodeId().nameSpaceIndex() != constants.OPCUA_NAMESPACE_ID:


        
        stringified_id = stringify_nodeid(expanded_node_id.nodeId() )
        if not stringified_id in added_nodes:
            
            nodeclass = get_attribute( client, expanded_node_id, attributeids.NodeClass, context)
            display_name = get_attribute( client, expanded_node_id, attributeids.DisplayName, context)
            browse_name = get_attribute( client, expanded_node_id, attributeids.BrowseName, context)

            if nodeclass == nodeclasses.Object:
                opcua_attributes = {
                    'NodeId':stringified_id, 
                    'BrowseName':browse_name, 
                    'DisplayName':display_name
                }
                document.append( nodeset_xml.make_element_for_uaobject( stringified_id, opcua_attributes, references, parent, refTypeFromParent  ) )
                
            elif nodeclass == nodeclasses.Variable:
                data_type = get_attribute( client, expanded_node_id, attributeids.DataType, context)
                access_level = get_attribute( client, expanded_node_id, attributeids.AccessLevel, context)
                opcua_attributes = {
                    'NodeId':stringified_id, 
                    'BrowseName':browse_name, 
                    'DisplayName':display_name,
                    'DataType':data_type,
                    'AccessLevel':access_level
                }
                document.append( nodeset_xml.make_element_for_uavariable( stringified_id, opcua_attributes, references, parent, refTypeFromParent  ) )

            elif nodeclass == nodeclasses.Method:
                executable = get_attribute( client, expanded_node_id, attributeids.Executable, context)
                opcua_attributes = {
                    'NodeId':stringified_id, 
                    'BrowseName':browse_name, 
                    'DisplayName':display_name,
                    'Executable':executable
                }
                document.append( nodeset_xml.make_element_for_uamethod( stringified_id, opcua_attributes, references, parent, refTypeFromParent  ) )
                
            else:
                print 'nodeclass not supported'
                context['errors'] += 1
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
    
    
