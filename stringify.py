from pyuaf.util import constants, opcuaidentifiers, nodeididentifiertypes

def stringify_nodeid( nodeid ):
    ns_idx = nodeid.nameSpaceIndex()
    if ns_idx>1:
        ns_idx = 1   # TODO make it a hack
    if nodeid.identifier().type == nodeididentifiertypes.Identifier_String:
        return "ns=" + str(ns_idx) + ";s=" + nodeid.identifier().idString
    elif nodeid.identifier().type == nodeididentifiertypes.Identifier_Numeric:
        return "ns=" + str(ns_idx) + ";i=" + str(nodeid.identifier().idNumeric)
    else:
        return "not-supported"
