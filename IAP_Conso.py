import re

# Define a function to read a file and split its contents into an array of lines
def read_lines(file):
    with open(file, 'r') as f:
        return f.read().splitlines()

# Read the contents of the "pylog" file into an array of lines
content = read_lines('./pylog')
"""
Instead of reading the contents of the "pylog" file into an array of lines
we can consider using protobuf here to convert IAP protofile to JSON (or YAML if possible)
but this might then require to rewrite at least a step (or two) later
"""
# Define an array to store the start and end indices of each exemption block
iterators = []
# Define an array to store the contents of each exemption block
blocks = []
# Define an array to store the account information for each exemption block
accounts = []

# THIS IS THE ORIGINAL CODE NEXT PLZ MERGE sIndex and eIndex for loop into split_blocks function!!
#def split_blocks(content):
#  """Splits the content of a file into blocks, where each block is defined by a start and end marker."""
#  blocks = []
#  start_marker = re.compile(r"exemption: {")
#  end_marker = re.compile(r"}")
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

# Sort the exemption blocks alphabetically
blocks.sort()

# Loop through each exemption block and extract the account information
for block in blocks:
    for b in block:
        if 'account: ' in b:
            accPos = block.index(b)
            block.pop(accPos)

            accounts.append(b)

# Define an array to store the unique exemption blocks
unique = []

# Loop through each exemption block and check if it is a duplicate
for i in range(len(blocks)-1):
    if blocks[i] == blocks[i+1]:
        # If the block is a duplicate, add the account information to the previous unique block
        if len(unique) <= 0:
            blocks[i].insert(-2, accounts[i])
            unique.append(blocks[i])
        else:
            unique[-1].insert(-3, accounts[i])
    else:
        # Catch the last block that was a duplicate in the first `if`; we still need an account from it
        if blocks[i] == blocks[i-1]:
            unique[-1].insert(-3, accounts[i])

        # If the block is not a duplicate, add it to the list of unique blocks
        blocks[i+1].insert(-2, accounts[i+1])
        unique.append(blocks[i+1])

        # Workaround for additional blocks that should be consolidated - DON'T USE!!!
        # if blocks[i] == blocks[i-2]:
            # unique[-1].insert(-3, accounts[i+2])


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

# OLD CODE (not sure what for, prolly just remove after confirming above works)
  # print("\n")
  # print('\033[96m ------------------------------  IAM-AP CONSOLIDATION  ------------------------------- \033[0m')
  
  # for unq in unique:
  #     for u in unq:
  #         if 'exemption' in u:
  #             print(f'\033[91m {u} \033[0m')
  #         elif 'account' in u:
  #             print(f'\033[93m{u} \033[0m')
  #         elif '}' in u:
  #             print(f'\033[91m{u} \033[0m')
  #         else:
  #             print(u)
  #     print('\n')
# OLD CODE END

# Convert YAML
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
# THIS IS THE ORIGINAL CODE all these functions need 2b checked whether they are already rewritten above!!
# def sort_blocks(blocks):
#   """Sorts the blocks of a file by their content."""
#   blocks.sort()
#   return blocks

# def extract_accounts(blocks):
#   """Extracts the account numbers from the blocks of a file."""
#   accounts = []

#   for block in blocks:
#     for line in block:
#       if "account: " in line:
#         account = line.split("account: ")[1]
#         accounts.append(account)

#   return accounts

# def remove_duplicates(blocks):
#   """Removes duplicate blocks from a list of blocks."""
#   unique_blocks = []

#   for i, block in enumerate(blocks):
#     if i == 0:
#       unique_blocks.append(block)
#     else:
#       if blocks[i-1] != block:
#         unique_blocks.append(block)

#   return unique_blocks

if __name__ == "__main__":
  content = read_lines("pylog")

  # blocks = split_blocks(content)
  # blocks = sort_blocks(blocks)

  yaml_convert(blocks)

  # accounts = extract_accounts(blocks)
  # blocks = remove_duplicates(blocks)

  print_blocks(unique)