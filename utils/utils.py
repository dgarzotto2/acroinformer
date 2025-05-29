# utils/utils.py

def summarize_entities_for_gpt(entities):
    names = ", ".join(entities.get("names", [])[:5])
    amounts = ", ".join(entities.get("amounts", [])[:3])
    keys = ", ".join(entities.get("registry_keys", [])[:3])
    dates = ", ".join(entities.get("dates", [])[:3])

    return f"Names: {names}; Amounts: {amounts}; Registry Keys: {keys}; Dates: {dates}"