import re

# Define a function that reads a file and split its contents into lines
def read_lines(file):
    with open(file, 'r') as f:
        return f.read().splitlines()


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
  # Catch the last block that was a duplicate in the first `if`; we still need an account from it
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
              # It helps with duplicate accounts in blocks
              if len(unique) > 1: 
                  unique[-1].insert(-3, accounts[i+1])
              else:
                  unique[-1].insert(-3, accounts[i])
      else:
          check_duplicate_accounts(blocks, accounts, unique, i)

          # Copy `blocks` table into `tmp` - copy is needed because if we insert account to a block, it will not match the next one from the list
          # Insert account from `accounts` table
          # Add block to `unique`
          tmp = blocks[i+1][:]
          tmp.insert(-2, accounts[i+1])
          unique.append(tmp)

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
  """
  Instead of reading the contents of the "pylog" file into an array of lines
  we can consider using protobuf here to convert IAP protofile to JSON (or YAML if possible)
  but this might then require to rewrite at least a step (or two) later
  """

  blocks = split_blocks(content)
  blocks.sort() # Sort the exemption blocks alphabetically

  # yaml_convert(blocks)

  accounts = extract_accounts(blocks)
  blocks = remove_duplicates(blocks, accounts)

  # remove_duplicate_accounts(unique)
  print_blocks(blocks)
