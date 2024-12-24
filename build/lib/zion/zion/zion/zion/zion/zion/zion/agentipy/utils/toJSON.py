import json


def to_json(s:str) -> dict:
    """
    Convert a string in the format `{key1:value1,key2:value2}` to a Python dictionary.
    
    Args:
        s (str): Input string to parse.

    Returns:
        dict: Parsed dictionary.

    Raises:
        ValueError: If the string cannot be parsed to a valid dictionary.
    """
    try:
        pairs = s.strip()[1:-1].split(",")

        obj = {}

        for pair in pairs:
            key, value = map(str.strip, pair.split(":"))

            if not key or value is None:
                raise ValueError("Invalid key-value pair format")
            
            obj[key] = int(value) if value.isdigit() else value
        return json.loads(json.dumps(obj))
    except Exception as e:
       raise ValueError(f"Failed to parse string to JSON:{e}")