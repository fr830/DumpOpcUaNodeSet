from lxml import etree

from pyuaf.util import Address, ExpandedNodeId, NodeId
from pyuaf.util import constants, opcuaidentifiers, nodeididentifiertypes

from stringify import stringify_nodeid

import pdb

def initialize_document():
    nsmap = {}
    nsmap[None] = 'http://opcfoundation.org/UA/2011/03/UANodeSet.xsd'
    root = etree.Element("UANodeSet", nsmap=nsmap )
    namespaceUris = etree.Element("NamespaceUris")
    uri = etree.Element("Uri")
    uri.text = "http://fix-your-company-name-here.org/MyProject/"  #  TODO namespace mapping should come from outside
    namespaceUris.append(uri)
    root.append(namespaceUris)

    return root

def writeout_document(document, path):
    output_file = file(path, 'w')  #  TODO: path should be configurable
    output_file.write( etree.tostring(document, pretty_print=True, xml_declaration=True, encoding='utf8') )

def make_element_for_uaobject(nodeid, browseName, references, parent, refTypeFromParent):
    if browseName == '':
        browseName = 'browsename-not-specified'
    element = etree.Element("UAObject", NodeId=nodeid, BrowseName=browseName)
    display_name = etree.Element("DisplayName")  # this is a hack actually
    display_name.text = browseName
    element.append (display_name)
    if len(references)>0 or parent.nodeId().nameSpaceIndex() == 0L:  # TODO constant
        element_references = etree.Element("References")
        if parent.nodeId().nameSpaceIndex() == 0L:
            root_ref = etree.Element("Reference", ReferenceType=stringify_nodeid(refTypeFromParent), IsForward="false")
            root_ref.text = stringify_nodeid( parent.nodeId() )
            element_references.append(root_ref)
        for reference in references:
            #pdb.set_trace()
            element_reference = etree.Element("Reference", ReferenceType=stringify_nodeid( reference.referenceTypeId ))
            element_reference.text = stringify_nodeid( reference.nodeId.nodeId() )
            element_references.append(element_reference)
            print reference
        element.append(element_references)
        
    return element
