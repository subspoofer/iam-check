import pandas as pd
import re

# Initialize a set to store unique blocks
unique_blocks = set()

# Read data from the "pylog" file
with open("pylog", "r") as file:
    data = file.read()

# Use regex to find all code blocks
code_blocks = re.findall(r'exemption: \{.*?\}', data, re.DOTALL)

# quick test of regex 
#print("Code Blocks:", code_blocks)

# Iterate through code blocks, extract the "block" value, and add to the set
for code_block in code_blocks:
    match = re.search(r'"block": "(.*?)"', code_block)
    if match:
        unique_blocks.add(match.group(1))

for block in unique_blocks:
    print(block)

# Set total unique exemption blocks and print
#total_unique_blocks = len(unique_blocks)
#print("Unique Exemption Blocks:", unique_blocks)
#print("Total Unique Blocks:", total_unique_blocks)


# create dataframe variable
#df = pd.DataFrame(data)

# Count unique exemption blocks and index them
#unique_blocks = df['exemption_block'].unique()
#total_unique_blocks = len(unique_blocks)

# Print the unique blocks and total count
#print("Unique Exemption Blocks:", unique_blocks)
#print("Total Unique Blocks:", total_unique_blocks)


#import difflib
#
#def identify_duplicate_permissions_and_accounts(pylog):
#  """Identifies duplicate permissions and accounts in a code file.
#
#  Args:
#    pylog: The path to the code file.
#
#  Returns:
#    A list of duplicate permissions and accounts.
#  """
#
#  # Parse the code file into a list of strings.
#  code_strings = []
#  with open(pylog, "r") as f:
#    for line in f:
#      code_strings.append(line)
#
#  # Compare each string in the list to the other strings.
#  duplicate_permissions_and_accounts = []
#  for i in range(len(code_strings)):
#    for j in range(i + 1, len(code_strings)):
#      diff = difflib.unified_diff(code_strings[i], code_strings[j], fromfile="Code", tofile="Code")
#      if diff == []:
#        # The two strings are identical.
#        duplicate_permissions_and_accounts.append((code_strings[i], code_strings[j]))
#
#  return duplicate_permissions_and_accounts