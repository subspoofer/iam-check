import re
# Define a function to read a file and split its contents into an array of lines
def read_lines(file):
    with open(file, 'r') as f:
        return f.read().splitlines()
    
# Read the contents of the "pylog" file into an array of lines
content = read_lines('./pylog')

# Define an array to store the start and end indices of each exemption block
iterators = []
# Define an array to store the contents of each exemption block
blocks = []
#accounts = []
# Define an array to store the account information for each exemption block
accounts_dict = {}
# Define an array to store the unique exemption blocks
unique = []
# Define an array to store the permissions of each exemption block
permissions = []

# Def a function to identify the start and end indices of each exemption block in the given list of strings
def index_blocks(content):
    sIndex, eIndex = None, None
    # Loop through the lines of the file and find the start and end indices of each exemption block
    for index, c in enumerate(content):
        if 'exemption: {' in c:
            sIndex = index
        if '}' in c:
            eIndex = index
            iterators.append({'sIndex': sIndex, 'eIndex': eIndex})
    return iterators

# Def a function to extract exemption blocks from the given list of strings using the given list of iterators
def extract_blocks(content, iterators):
    for it in iterators:
        segment = []
        for i in range(it['sIndex'], it['eIndex']+1):
            segment.append(content[i])

        blocks.append(segment)
        # Print test to see start and end of indices in each block
        print(f"Block {len(blocks)}: start index {it['sIndex']}, end index {it['eIndex']}")
        print(segment, '\n')
    return blocks

# Now find the start and end indices of each exemption block in the file
iterators = index_blocks(content)

# Extract the exemption blocks from the file using the iterators
blocks = extract_blocks(content, iterators)

# How did this end up here, what is it for? I see no use of this method here
#blocks.sort()

# Print the resulting blocks
print('Blocks Extraction Test \n', blocks, '\n')

# Define a function to extract accounts from each block
def extract_account(blocks):
    for i, block in enumerate(blocks):
        for j, b in enumerate(block):
            if 'account: ' in b:
                accounts_dict[i] = b
                block.pop(j)
                print("Found account", b)
    return accounts_dict

# Extract the account information from the blocks
accounts_dict = extract_account(blocks)

print('\n Extracted Accounts \n', accounts_dict)

# This is to figure out for laterzzz
# # Define a function to identify permission sets in each exemption block
# def identify_permissions(blocks):
#     for block in blocks:
#         for b in block:
#             if 'permission: ' in b:
#                 permPos = block.index(b)
#                 block.pop(permPos)
#                 permissions.append(b)
#     return permissions

# # Identify the permission sets in each block
# permissions = identify_permissions(blocks)
# print(permissions, '\n')

blocks.sort()

def check_duplicate(blocks):
    print(f"Number of blocks: {len(blocks)}")
    for i, block in enumerate(blocks[0:-1]):
        print(f"Checking block {i}: {block}")
        if blocks[i] == blocks[i+1]:
            print(f"Found duplicate block: {block}")
            # If the block is a duplicate, add the account information to the previous unique block
            if len(unique) <= 0:
                block.insert(-2, accounts_dict[i])
                unique.append(block)
                print(f"Added block {block} to unique list")
            else:
                # Use the accounts_dict to add the correct account information to the previous unique block
                unique[-1].insert(-3, accounts_dict[i+1])
                print(f"Added account {accounts_dict[i+1]} to previous unique block:")
                print(f"Previous unique block: {unique[-1]}")
        else:
            # If the block is not a duplicate, create a copy of the next block and add the account information to the copy
            tmp = blocks[i+1][:]
            tmp.insert(-2, accounts_dict[i+1])
            unique.append(tmp)
            print(f"Created copy of block {blocks[i+1]} and added account {accounts_dict[i+1]} to copy:")
            print(f"Copy: {tmp}")
    return unique if unique is not None else []
    
# Check for duplicates
unique = check_duplicate(blocks)

# Print the consolidated exemption blocks and account information to the console
def print_blocks(blocks):
  print("\n")
  print('\x1b[96m ------------------------------  IAM-AP CONSOLIDATION  ------------------------------- \x1b[0m')
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

if __name__ == "__main__":
  content = read_lines("pylog")
  print_blocks(unique)