import os

# Define a function to read a file and split its contents into an array of lines
def read_lines(file):
    with open(file, 'r') as f:
        return f.read().splitlines()

# Read the contents of the "pylog" file into an array of lines
content = read_lines('./pylog')

# Define variables to keep track of the start and end indices of each exemption block
sIndex, eIndex = None, None

# Define an array to store the start and end indices of each exemption block
iterators = []

# Loop through the lines of the file and find the start and end indices of each exemption block
for index, c in enumerate(content):
    if 'exemption: {' in c:
        sIndex = index
    if '}' in c:
        eIndex = index
        iterators.append({'sIndex': sIndex, 'eIndex': eIndex})

# Define an array to store the contents of each exemption block
blocks = []

# Loop through the start and end indices of each exemption block and extract the contents of each block
for it in iterators:
    segment = []
    for i in range(it['sIndex'], it['eIndex']+1):
        segment.append(content[i])

    blocks.append(segment)

# Sort the exemption blocks alphabetically
blocks.sort()

# Define an array to store the account information for each exemption block
accounts = []

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
for i in range(1, len(blocks)):
    if blocks[i] == blocks[i-1]:
        # If the block is a duplicate, add the account information to the previous unique block
        if len(unique) <= 0:
            blocks[i-1].insert(-2, accounts[i-1])
            unique.append(blocks[i-1])
        else:
            unique[-1].insert(-3, accounts[i-1])
    else:
        # If the block is not a duplicate, add it to the list of unique blocks
        blocks[i-1].insert(-2, accounts[i-1])
        unique.append(blocks[i-1])

# Print the consolidated exemption blocks and account information to the console
print("\n")
print('\033[96m ------------------------------  IAM-AP CONSOLIDATION  ------------------------------- \033[0m')

for unq in unique:
    for u in unq:
        if 'exemption' in u:
            print(f'\033[91m {u} \033[0m')
        elif 'account' in u:
            print(f'\033[93m{u} \033[0m')
        elif '}' in u:
            print(f'\033[91m{u} \033[0m')
        else:
            print(u)
    print('\n')

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



if __name__ == "__main__":
  content = read_lines("pylog")

  blocks = split_blocks(content)
  blocks = sort_blocks(blocks)

  yaml_convert(blocks)

  accounts = extract_accounts(blocks)
  blocks = remove_duplicates(blocks)

  print_blocks(blocks)
