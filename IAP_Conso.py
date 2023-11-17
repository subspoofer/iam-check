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
  # List to store the start and end indices of each exemption block
  iterators = []
  # List to store the contents of each exemption block
  blocks = []
  
  # Define variables to keep track of the start and end indices of each exemption block
  sIndex, eIndex = None, None
  # Loop through the lines of the file and find the start and end indices of each exemption block
  for index, c in enumerate(content):
      if 'exemption: {' in c:
          sIndex = index
      if '}' in c:
          eIndex = index
          iterators.append({'sIndex': sIndex, 'eIndex': eIndex})

  # Loop through the start and end indices of each exemption block and extract the contents of each block
  for it in iterators:
      segment = []
      for i in range(it['sIndex'], it['eIndex']+1):
          segment.append(content[i])

      blocks.append(segment)

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
def remove_duplicates(blocks, accounts):
  # Define an array to store the unique exemption blocks
  unique = []

  # Loop through each exemption block and check if it is a duplicate
  for i, block in enumerate(blocks[0:-1]):
      if blocks[i] == blocks[i+1]:
          # If the block is a duplicate, add the account information to the previous unique block
          if len(unique) <= 0:
              blocks[i].insert(-2, accounts[i])
              unique.append(blocks[i])
          else:
              # this helps with duplicate accounts in blocks
              if len(unique) > 1: 
                  unique[-1].insert(-3, accounts[i+1])
              else:
                  unique[-1].insert(-3, accounts[i])
      else:
          check_duplicate_accounts(blocks, accounts, unique, i)

          # Copy `blocks` table into `tmp` - needed because if we insert account in a block, it will not match the next one from the list
          tmp = blocks[i+1][:]
          tmp.insert(-2, accounts[i+1]) # Insert account from `accounts` table
          unique.append(tmp) # Add block to `unique`

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

# Define a function to sort the lines within each block
def sort_lines_in_blocks(blocks):
    for i in range(len(blocks)):
        # Separate the opening and closing braces from the rest of the block
        opening_brace = blocks[i].pop(0)
        closing_brace = blocks[i].pop(-1)

        # Separate permissions and accounts
        permissions = [line for line in blocks[i] if line.strip().startswith('permission')]
        accounts = [line for line in blocks[i] if line.strip().startswith('account')]

        # Sort permissions and accounts
        permissions.sort()
        accounts.sort(key=lambda x: x.lower())  # sort accounts case-insensitively

        # Combine sorted permissions and accounts
        blocks[i] = permissions + accounts

        # Add the opening and closing braces back to the block
        blocks[i].insert(0, opening_brace)
        blocks[i].append(closing_brace)

    return blocks

# Generate output
if __name__ == "__main__":
  # Read the contents of the "pylog" file into an array of lines
  content = read_lines('./pylog')
  blocks = split_blocks(content)
  blocks.sort() # Sort the exemption blocks alphabetically

  # yaml_convert(blocks)

  accounts = extract_accounts(blocks)
  blocks = remove_duplicates(blocks, accounts)

  # Sort the lines within each block
  blocks = sort_lines_in_blocks(blocks)

  # remove_duplicate_accounts(unique)
  print_blocks(blocks)