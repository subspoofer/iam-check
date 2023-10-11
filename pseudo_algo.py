import re

# Open and read the file "pylog"
with open("pylog", "r") as f:
    data = f.read()

# Define a regular expression pattern to match the exemption blocks
exemption_blocks = re.findall(r'exemption: \{.*?\}', data, re.DOTALL)

# Define a regular expression pattern to extract the unique identifier for each block
identifier_pattern = r'exemption: \{(.+?)\}'

# Create a dictionary to store the unique identifiers and their corresponding exemption blocks
exemption_dict = {}

# Loop through the exemption blocks and extract the unique identifier for each block
for block in exemption_blocks:
    identifier_match = re.search(identifier_pattern, block)
    if identifier_match:
        identifier = identifier_match.group(1)
        exemption_dict[identifier] = block

# Print each exemption block with a number
#for i, block in enumerate(exemption_blocks):
#   print(f"Exemption block {i+1}: {block}")

# Define a regular expression pattern to extract the permission sets
permission_pattern = r'permission: "(.+?)"'

# Identify the permissions sets that have duplicates
duplicate_permissions = []

# Loop through the exemption blocks and extract permission sets that have duplicates
for block in exemption_blocks:
    permission_match = re.search(permission_pattern, block)
    if permission_match:
        permission = permission_match.group(1)
        if permission in duplicate_permissions:
            continue
        else:
            duplicate_permissions.append(permission)

# Print each duplicate permission set with a number
#for i, permission in enumerate(duplicate_permissions):
#    print(f"Duplicate permission {i+1}: {permission}")
