import re

# Define a function that reads a file and split its contents into lines
def read_lines(file):
    with open(file, 'r') as f:
        return f.read().splitlines()

"""
consider using protobuf here to convert IAP protofile to YAML if possible
"""


# Define a function to split and index (start/end) all the exemption blocks
def split_blocks(content):
    blocks = []
    sIndex, eIndex = None, None
    for index, c in enumerate(content):
        if 'exemption: {' in c:
            sIndex = index
        if '}' in c:
            eIndex = index
            block = content[sIndex:eIndex+1]
            permissions = [line for line in block if "permission" in line]
            account = [line for line in block if "account" in line][0]
            blocks.append({'sIndex': sIndex, 'eIndex': eIndex, 'permissions': permissions, 'account': account})
    return blocks


# Define function that extracts all the accounts from exemption blocks
def extract_accounts(blocks):
  # Define a list to store the account information for each exemption block
  accounts = []

  # Loop through each exemption block and extract the account information
  for block in blocks:
      for b in block:
          if 'account: ' in b:
              accPos = block.index(b)
              block.pop(accPos)

              accounts.append(b)
  
  return accounts

# Define function that checks for duplicate accounts
def check_duplicate_accounts(blocks, accounts, unique, index):
  # Catch the last duplicate block in the first iteration if we still need to extract an account from it
  if blocks[index] == blocks[index-1]:
      if any(accounts[index] in a for a in unique[-1]):
        return
      else:
        unique[-1].insert(-3, accounts[index])

# Define function used to remove duplicate exemption blocks
def remove_duplicates(blocks):
    if not blocks:
        return []
    blocks.sort(key=lambda x: (x['permissions'], x['account']))
    unique = [blocks[0]]
    for block in blocks[1:]:
        if block['permissions'] != unique[-1]['permissions'] or block['account'] != unique[-1]['account']:
            unique.append(block)
    return unique


# Print the consolidated exemption blocks and account information to the console
def print_blocks(blocks):
  print("\n")
  print('\x1b[96m ------------------------------  IAM-AP CONSOLIDATION  ------------------------------- \x1b[0m')
# might have switched "blocks" here to "unique" at this point, need to check
  for block in blocks:
    for line in block:
      if "exemption" in line:
        print(f"\x1b[91m {line} \x1b[0m")
      elif "account" in line:
        print(f"\x1b[93m{line} \x1b[0m")
      elif "}" in line:
        print(f"\x1b[91m{line} \x1b[0m")
      else:
        print(line)

    print("\n")

# Convert to YAML
def yaml_convert(blocks):
  # Clear file from previous run
  f = open("iap.yaml", "w")
  f.write('')
  f.close()

  for block in blocks:
    # Append data
    f = open("iap.yaml","a")
    f.write('- exemption:\n')

    perms = [b for b in block if re.search(r'\b' + "permission" + r'\b', b)]
    for perm in perms: 
      f.write('  -' + perm[1:] + '\n')

    accounts = [b for b in block if re.search(r'\b' + "account" + r'\b', b)]
    for account in accounts: 
      f.write('  -' + account[1:] + '\n')

    f.write('\n')
    f.close()

# Generate output
if __name__ == "__main__":
  # Read the contents of the "pylog" file into an array of lines
  content = read_lines('./pylog')
  blocks = split_blocks(content)
  #blocks.sort() # Sort the exemption blocks alphabetically

  blocks = sorted(blocks, key=lambda block: (block['permissions'], block['account']))

  # yaml_convert(blocks)

  accounts = extract_accounts(blocks)
  blocks = remove_duplicates(blocks)

  # remove_duplicate_accounts(unique)
  print_blocks(blocks)