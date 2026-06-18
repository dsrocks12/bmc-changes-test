import json
import re

def format_key_label(key):
    if not key:
        return ""
    if "." in key:
        return key
    # Split camelCase and convert underscores to spaces
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1 \2', key)
    s2 = re.sub('([a-z0-9])([A-Z])', r'\1 \2', s1)
    s3 = s2.replace("_", " ")
    return " ".join(w.capitalize() for w in s3.split() if w)

def ensure_punctuation(text):
    if not isinstance(text, str):
        return text
    t = text.strip()
    if not t:
        return text
    if re.search(r'[a-zA-Z0-9)]$', t):
        return t + "."
    return t

def flatten_dict(item, parent_key=""):
    flat = {}
    if isinstance(item, dict):
        for key, value in item.items():
            new_key = f"{parent_key}.{key}" if parent_key else key
            flat.update(flatten_dict(value, new_key))
    else:
        flat[parent_key] = item
    return flat

def build_markdown_table(headers, rows):
    header_line = "| " + " | ".join(headers) + " |"
    separator = "| " + " | ".join("---" for _ in headers) + " |"
    lines = [header_line, separator]
    for row in rows:
        cells = []
        for h in headers:
            val = row.get(h, "")
            val_str = str(val).replace("|", "\\|").replace("\n", " ")
            cells.append(val_str)
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)

def get_singular_noun(api):
    api_id = api.get("id", "")
    if "agentless" in api_id.lower():
        return "Agentless Host"
    if "param" in api_id.lower():
        return "Parameter"
    if "host" in api_id.lower():
        return "Host"
    if "profile" in api_id.lower():
        return "Profile"
    if "agent" in api_id.lower():
        return "Agent"
    return "Key"

def format_api_response(api, raw_response):
    """
    Generic dynamic formatter for API responses.
    Returns a formatted string (table or list) if it should be displayed as a table,
    otherwise returns None to fallback to natural language explanation.
    """
    # 1. Parse JSON
    try:
        payload = json.loads(raw_response)
    except Exception:
        return None

    if not isinstance(payload, dict):
        return None

    if not payload.get("success"):
        return None

    noun = get_singular_noun(api)
    plural_noun = noun + "s" if not noun.endswith("s") else noun
    if noun.lower() == "host":
        plural_noun = "hosts"

    data = payload.get("data")
    if data is None or data == "" or data == [] or data == {}:
        # If there's a top-level message/description on success, return it directly
        msg = payload.get("message") or payload.get("description")
        if msg:
            return ensure_punctuation(msg)
        if noun != "Key":
            return ensure_punctuation(f"No {plural_noun.lower()} were found")
        return ensure_punctuation(f"Request successfully executed (Status Code: {payload.get('status_code', 200)})")

    # Extract primary list if data is a dict with a single list key
    if isinstance(data, dict) and len(data) == 1:
        key = list(data.keys())[0]
        if isinstance(data[key], list):
            data = data[key]

    def format_value(val, depth=0):
        if val is None or val == "" or val == [] or val == {}:
            return ""

        if isinstance(val, list):
            if not val:
                return ""
            
            # Check if list contains only primitives
            if all(not isinstance(item, (dict, list)) for item in val):
                return "\n".join(f"• {item}" for item in val)

            # Check if this is a list of dicts where at least one dict has a multiline value
            is_multiline_list = False
            for item in val:
                if isinstance(item, dict):
                    for k, v in item.items():
                        if isinstance(v, str) and "\n" in v:
                            is_multiline_list = True
                            break
                if is_multiline_list:
                    break

            if is_multiline_list:
                blocks = []
                for item in val:
                    if not isinstance(item, dict):
                        blocks.append(f"• {item}")
                        continue
                    
                    item_lines = []
                    header_key = None
                    for hk in ["testname", "name", "title", "id"]:
                        for k in item.keys():
                            if k.lower() == hk:
                                header_key = k
                                break
                        if header_key:
                            break
                    
                    status_key = None
                    for sk in ["status", "success", "state"]:
                        for k in item.keys():
                            if k.lower() == sk:
                                status_key = k
                                break
                        if status_key:
                            break
                    
                    if header_key and status_key:
                        h_val = item[header_key]
                        s_val = item[status_key]
                        item_lines.append(f"• **{h_val}**: {s_val}")
                    elif header_key:
                        item_lines.append(f"• **{item[header_key]}**")
                    
                    for k, v in item.items():
                        if k in (header_key, status_key):
                            continue
                        if v is None or v == "" or v == [] or v == {}:
                            continue
                        k_title = format_key_label(k)
                        v_str = str(v).strip()
                        if "\n" in v_str:
                            item_lines.append(f"• **{k_title}**:\n```\n{v_str}\n```")
                        else:
                            if k.lower() in ("message", "description", "msg"):
                                v_str = ensure_punctuation(v_str)
                            item_lines.append(f"• **{k_title}**: {v_str}")
                    
                    blocks.append("\n".join(item_lines))
                return "\n\n".join(blocks)

            rows = []
            all_keys = set()
            for item in val:
                if isinstance(item, dict):
                    flat_item = flatten_dict(item)
                    rows.append(flat_item)
                    all_keys.update(flat_item.keys())
                else:
                    rows.append({noun: item})
                    all_keys.add(noun)

            if not rows:
                return ""

            priority = ["name", "id", "status", "type", "profile", "host", "value", "agent", "server"]
            def key_priority(k):
                k_low = k.lower()
                for idx, pk in enumerate(priority):
                    if k_low == pk or k_low.endswith("." + pk) or k_low.startswith(pk + "."):
                        return idx
                return len(priority)

            ordered_keys = sorted(list(all_keys), key=lambda k: (key_priority(k), k.lower()))

            return build_markdown_table(ordered_keys, rows)

        elif isinstance(val, dict):
            simple_fields = {}
            multiline_fields = {}
            complex_fields = {}

            for k, v in val.items():
                if isinstance(v, (dict, list)):
                    complex_fields[k] = v
                elif isinstance(v, str) and "\n" in v:
                    multiline_fields[k] = v
                else:
                    simple_fields[k] = v

            parts = []
            if simple_fields:
                if len(simple_fields) == 1:
                    k, v = list(simple_fields.items())[0]
                    if k.lower() in ("message", "description", "msg", "info", "errormessage", "successmessage"):
                        parts.append(ensure_punctuation(str(v)))
                    else:
                        parts.append(f"**{format_key_label(k)}**: {v}")
                else:
                    key_header = "Property"
                    if noun == "Parameter":
                        key_header = "Parameter"
                    elif noun == "Key":
                        key_header = "Key"
                    
                    rows = []
                    for k, v in sorted(simple_fields.items()):
                        rows.append({key_header: k, "Value": str(v)})
                    parts.append(build_markdown_table([key_header, "Value"], rows))

            if multiline_fields:
                for k, v in sorted(multiline_fields.items()):
                    v_clean = str(v).strip()
                    parts.append(f"**{format_key_label(k)}:**\n```\n{v_clean}\n```")

            if complex_fields:
                for k, v in sorted(complex_fields.items()):
                    if v in ([], {}):
                        continue
                    parts.append(f"**{format_key_label(k)}:**")
                    formatted_complex = format_value(v, depth + 1)
                    if formatted_complex:
                        parts.append(formatted_complex)

            return "\n\n".join(p for p in parts if p)

        else:
            val_str = str(val)
            if "\n" in val_str:
                return f"```\n{val_str.strip()}\n```"
            return val_str

    formatted_data = format_value(data)
    if not formatted_data:
        return None

    msg = payload.get("message") or payload.get("description")
    msg_prefix = ensure_punctuation(msg) + "\n\n" if msg else ""

    if isinstance(data, list):
        count = len(data)
        item_word = noun.lower() if count == 1 else plural_noun.lower()
        return f"{msg_prefix}Found {count} {item_word}:\n\n{formatted_data}"
    
    if isinstance(data, dict):
        return f"{msg_prefix}{formatted_data}"

    return f"{msg_prefix}{formatted_data}"
