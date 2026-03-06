import json
import orjson

def parse_workflow(data):
    """
    Parses ComfyUI workflow JSON data into a structured dictionary.
    
    Args:
        data (dict | str): The parsed JSON dict from png_metadata, or a JSON string.
        
    Returns:
        dict: A dictionary mapping node IDs to their type and inputs.
              Format: { "node_id": { "type": "node_type", "inputs": { "key": "value" } } }
    """
    if isinstance(data, str):
        try:
            data = orjson.loads(data)
        except orjson.JSONDecodeError as e:
            print(f"Error decoding JSON data: {e}")
            return {}

    if not isinstance(data, dict):
        return {}

    parsed_nodes = {}
    
    # ComfyUI 'prompt' format usually looks like:
    # { "1": {"inputs": {...}, "class_type": "KSampler", "_meta": {...}}, "2": {...} }
    # ComfyUI 'workflow' format might look like:
    # { "nodes": [ {"id": 1, "type": "KSampler", "widgets_values": [...], "inputs": [...]}, ... ], "links": [...] }
    
    # We need to handle the 'prompt' format which is typical for parameters being fed into the execution
    # and what's usually requested to be diffed. 
    # If the input contains "nodes" as a list, it's the UI workflow format, which is harder to map directly 
    # to key/value parameters without the prompt execution format.
    # Usually, `img.info['prompt']` contains the key/value execution parameters we want.
    
    if isinstance(data, dict) and 'nodes' in data and isinstance(data['nodes'], list):
         # UI Workflow format parsing
        for node in data['nodes']:
            node_id = str(node.get('id', ''))
            if not node_id:
                continue
                
            node_type = node.get('type', 'Unknown')
            node_title = node.get('title', node_type)
            
            # Extract inputs (this can be complex in UI workflow as widgets are positional lists)
            inputs = {}
            if 'widgets_values' in node:
                # We don't have the keys for these in the UI workflow format easily, 
                # so we will just index them. This is why `img.info['prompt']` is preferred.
                for i, val in enumerate(node['widgets_values']):
                    inputs[f"widget_{i}"] = val
                    
            parsed_nodes[node_id] = {
                "type": node_type,
                "title": node_title,
                "inputs": inputs
            }
            
    elif isinstance(data, dict):
        # Prompt execution format parsing (Preferred for parameter diffing)
        # Assuming keys are node IDs
        for node_id, node_data in data.items():
            if not isinstance(node_data, dict):
                continue
                
            node_type = node_data.get('class_type', 'Unknown')
            
            # Extract title from _meta if it exists
            node_title = node_type
            if '_meta' in node_data and isinstance(node_data['_meta'], dict):
                node_title = node_data['_meta'].get('title', node_type)
                
            inputs = node_data.get('inputs', {})
            
            # Sometimes inputs contain nested lists/dicts linking to other nodes.
            # We will flatten or keep them as string representations for the UI.
            cleaned_inputs = {}
            for k, v in inputs.items():
                if isinstance(v, list) and len(v) == 2 and isinstance(v[0], str):
                     # This is a link to another node's output: ["node_id", output_index]
                     cleaned_inputs[k] = f"Link -> Node {v[0]} [{v[1]}]"
                else:
                    cleaned_inputs[k] = v

            parsed_nodes[str(node_id)] = {
                "type": node_type,
                "title": node_title,
                "inputs": cleaned_inputs
            }

    return parsed_nodes

