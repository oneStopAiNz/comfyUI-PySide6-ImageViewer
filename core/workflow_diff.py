def compare_nodes(nodeA, nodeB):
    """
    Compares the inputs of two ComfyUI nodes to find differences.
    We assume the two nodes have already been parsed into the structured format
    from `core.comfy_parser.parse_workflow`.
    
    Args:
        nodeA (dict): First node's data {"type": str, "inputs": dict}
        nodeB (dict): Second node's data {"type": str, "inputs": dict}
        
    Returns:
        list: A list of parameter keys (strings) that are different between the two nodes.
              A parameter is considered different if:
              1. It exists in one but not the other.
              2. The value is different between the two.
              (Note: If the node types are fundamentally different, we could return all keys,
               but the UI probably just highlights what changed on the *current* selection, 
               so it's better to return the keys from nodeA/nodeB that don't match).
    """
    if not isinstance(nodeA, dict) or not isinstance(nodeB, dict):
        return []

    # Get the inputs
    inputsA = nodeA.get('inputs', {})
    inputsB = nodeB.get('inputs', {})
    
    changed_keys = []
    
    # Check what's in A that differs from B or is missing in B
    for key, valA in inputsA.items():
        if key not in inputsB:
            changed_keys.append(key)
        else:
            if inputsB[key] != valA:
                changed_keys.append(key)
                
    # Check what's new in B that wasn't in A
    for key in inputsB.keys():
        if key not in inputsA:
            changed_keys.append(key)
            
    # Remove duplicates if any logic above caused it (unlikely with this specific dict iteration, but safe)
    return list(set(changed_keys))
