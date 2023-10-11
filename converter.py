import yaml
import re

# read pylog file and store it in pylog var
with open('pylog', 'r') as f:
    pylog = f.read()

# # define regular expressions to match the custom format
# regex_dict = re.compile(r'\{(?P<dict>.*?)\}')
# regex_list = re.compile(r'\[(?P<list>.*?)\]')
# regex_key_value = re.compile(r'(?P<key>[^:]+):\s*(?P<value>.+)')

def parse_custom_format(data):
    # split the data into lines
    lines = data.split("\n")
    # initialize an empty list to store the parsed data
    parsed_data = []
    # initialize an empty dictionary to store the current exemption data
    current_exemption = {}
    # iterate over the lines
    for line in lines:
        # ignore lines starting with #
        if line.startswith("#"):
            continue
        # remove { and } characters
        line = line.replace("{", "").replace("}", "")
        # check if the line starts with exemption
        if line.startswith("exemption"):
            # if there is already an exemption being parsed, add it to the parsed data
            if current_exemption:
                parsed_data.append(current_exemption)
                current_exemption = {}
            # add the exemption key to the current exemption dictionary
            current_exemption["exemption"] = []
            # add the permission key to the current exemption dictionary
            current_exemption["permission"] = []
            # add the account key to the current exemption dictionary
            current_exemption["account"] = ""
            # add the line to the exemption list
            current_exemption["exemption"].append(line.replace("exemption:", "").strip())
        # check if the line starts with double space indentation
        elif line.startswith("  "):
            # add the line to the exemption list
            current_exemption["exemption"].append(line.strip())
        # check if the line contains permission or account
        elif "permission:" in line or "account:" in line:
            # split the line into key and value
            key, value = line.split(":")
            # remove leading and trailing whitespace from the value
            value = value.strip()
            # add the value to the current exemption dictionary
            if "permission" in key:
                current_exemption["permission"].append(value)
            elif "account" in key:
                current_exemption["account"] = value
    # add the last exemption to the parsed data
    if current_exemption:
        parsed_data.append(current_exemption)
    return parsed_data

# # define a function to recursively parse the custom format
# def parse_custom_format(data):
#     # check if the data is a dictionary
#     if data.startswith("exemption:"):
#         dict_data = {}
#         for line in data.split("\n"):
#             line = line.strip()
#             if line.startswith("permission:"):
#                 dict_data.setdefault("permission", []).append(line.split(":")[1].strip())
#             elif line.startswith("account:"):
#                 dict_data["account"] = line.split(":")[1].strip()
#         return dict_data
#     # check if the data is a list
#     elif data.startswith("# Permission to manage firewall rules."):
#         list_data = []
#         for item in data.split("# Permission to manage firewall rules.")[1:]:
#             item_data = parse_custom_format(item.strip())
#             if item_data:
#                 list_data.append({"exemption": item_data})
#         return list_data
#     # otherwise, assume the data is a scalar value
#     return data.strip()

# parse the pylog data to a Python object
pylog_data = parse_custom_format(pylog)

# convert pylog data to YAML data
yaml_data = yaml.dump(pylog_data)

# write YAML data to .yaml file
with open('pylog.yaml', 'w') as f:
    f.write(yaml_data)