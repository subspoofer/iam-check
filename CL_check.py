import re
import subprocess
from enum import Enum

cl = input("Enter the CL number: ")
command = f'g4 list -s {cl} | cut -c16- | awk \'{{cmd="p4 g4d {cl}"; cmd | getline output; close(cmd); print output $0}}\''
output = subprocess.check_output(command, shell=True, text=True)
files = output.strip().split('\n')


class Role:
    keywords = ["setIamPolicy", "roles/owner", "roles/editor", "roles/viewer", "iam.serviceAccounts.actAs"]
    def __init__(self, line_number, role):
        self.line_number = line_number
        self.role = role

class Account:
    keywords = ["mdb:", "user:", "@google.com"]
    def __init__(self, line_number, account):
        self.line_number = line_number
        self.account = account

class File:
    keywords = ["iam_allowed_policy.textproto", "iam_policy.yaml", "project.yaml"]
    wildcards = [".*", "/*", "*."]
    def __init__(self, line_number, wildcard):
        self.line_number = line_number
        self.wildcard = wildcard


checks = {
    "roles": {},
    "accounts": {},
    "wildcards": {}
}


def read_files():
    if len(files) <= 0: return

    print(f"\033[96m--------------------------------------  FILES ---------------------------------------\033[0m")
    for file in files:
        found_file = [f for f in File.keywords if f in file]
        if not found_file: print("File not found")
        else: print(f"{file[file.find('/google.com'):file.find(found_file[0])]}\033[92m{found_file[0]}\033[0m")


    for file_path in files:
        try:
            with open(file_path, "r") as file:
                content = file.read().split('\n')
                line_number = 0

                for line in content:
                    line_number += 1

                    # Skip lines that contain '#'
                    if '#' in line:
                        continue

                    found_role = [role for role in Role.keywords if role in line]
                    found_account = [account for account in Account.keywords if account in line]
                    found_wildcard = [wildcard for wildcard in File.wildcards if wildcard in line]

                    # Map values
                    if found_role:
                        if file_path not in checks["roles"]: checks["roles"][file_path] = []
                        checks["roles"][file_path].append(Role(line_number, line))

                    if found_account:
                        if file_path not in checks["accounts"]: checks["accounts"][file_path] = []
                        checks["accounts"][file_path].append(Account(line_number, line))
                
                    if found_wildcard:
                        if file_path not in checks["wildcards"]: checks["wildcards"][file_path] = []
                        checks["wildcards"][file_path].append(File(line_number, line))

        except FileNotFoundError:
            print(f"\033[91mFile not found:\033[0m {file_path[file_path.find('/google.com'):]}")


def print_roles():
    if len(checks["roles"].items()) <= 0: return

    # Print roles
    print(f"\n\033[96m--------------------------------------  ROLES ---------------------------------------\033[0m")
    for file_path, roles in checks["roles"].items():
        print(f"\033[92mPermissions found in file\033[0m '{file_path[file_path.find('/google.com'):]}':")
        for role in roles:
            print(f"\033[93mLine {role.line_number}: \033[91m{role.role.strip()}\033[0m")

def print_accounts():
    if len(checks["accounts"].items()) <= 0: return
    
    # Print accounts
    print(f"\n\033[96m-------------------------------  ACCOUNTS && GROUPS --------------------------------\033[0m")
    for file_path, accounts in checks["accounts"].items():
        print(f"\033[92mAccounts found in file\033[0m '{file_path[file_path.find('/google.com'):]}':")
        for account in accounts:
            print(f"\033[93mLine {account.line_number}: \033[91m{account.account.strip()}\033[0m")

def print_wildcards():
    if len(checks["wildcards"].items()) <= 0: return

    # Print wildcards in .textproto
    print(f"\n\033[96m-----------------------------------  WILDCARDS  ------------------------------------\033[0m")
    for file_path, wildcards in checks["wildcards"].items():
        print(f"\033[92mWildcards found in file\033[0m '{file_path[file_path.find('/google.com'):]}':")
        for wildcard in wildcards:
            print(f"\033[93mLine {wildcard.line_number}: \033[91m{wildcard.wildcard.strip()}\033[0m")


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
      if 'exemption' in c:
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
  # If first two blocks are unique they need to be handled separately
  if index == 0:
     blocks[0].insert(-2, accounts[0])
     unique.append(blocks[0])
     return

  # Catch the last duplicate block in the first iteration; its account is still needed
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
              if len(unique) == 1: 
                  unique[-1].insert(-3, accounts[i])
              else:
                  unique[-1].insert(-3, accounts[i+1])
      else:
          check_duplicate_accounts(blocks, accounts, unique, i)

          # Copy blocks table into tmp - needed when an account is inserted into a block to match the one from the list
          tmp = blocks[i+1][:]
          tmp.insert(-2, accounts[i+1]) # Insert account from `accounts` table
          unique.append(tmp) # Add block to `unique`

  return unique


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

# # Convert to YAML
# def yaml_convert(blocks):
#   # Clear file from previous run
#   f = open("iap.yaml", "w")
#   f.write('')
#   f.close()

#   for block in blocks:
#     # Append data
#     f = open("iap.yaml","a")
#     f.write('- exemption:\n')

#     perms = [b for b in block if re.search(r'\b' + "permission" + r'\b', b)]
#     for perm in perms: 
#       f.write('  -' + perm[1:] + '\n')

#     accounts = [b for b in block if re.search(r'\b' + "account" + r'\b', b)]
#     for account in accounts: 
#       f.write('  -' + account[1:] + '\n')

#     f.write('\n')
#     f.close()

# Define a function to sort the lines within each block
def sort_lines_in_blocks(blocks):
    for i in range(len(blocks)):
        # Separate the opening and closing braces from the rest of the block
        opening_brace = blocks[i].pop(0)
        closing_brace = blocks[i].pop(-1)

        # Separate permissions and accounts
        permissions = [line for line in blocks[i] if line.strip().startswith('permission')]
        roles = [line for line in blocks[i] if line.strip().startswith('role')]
        accounts = [line for line in blocks[i] if line.strip().startswith('account')]

        # Sort permissions and accounts
        permissions.sort()
        accounts.sort(key=lambda x: x.lower())  # sort accounts case-insensitively

        # Combine sorted permissions and accounts
        if len(roles) > 0:
            blocks[i] = permissions + roles + accounts
        else:
            blocks[i] = permissions + accounts

        # Add the opening and closing braces back to the block
        blocks[i].insert(0, opening_brace)
        blocks[i].append(closing_brace)

    return blocks

# Generate output
if __name__ == "__main__":
    read_files()
    print_roles()
    print_accounts()
    print_wildcards()

    # Loop through each iam_allowed_policy.textproto file
    for file_path in files:
        # Check if the file is an iam_allowed_policy.textproto file
        if "iam_allowed_policy.textproto" in file_path:
            # Read the contents of the file into an array of lines
            content = read_lines(file_path)
            blocks = split_blocks(content)
            blocks.sort() # Sort the exemption blocks alphabetically

            accounts = extract_accounts(blocks)
            blocks = remove_duplicates(blocks, accounts)

            # Sort the lines within each block
            blocks = sort_lines_in_blocks(blocks)

            # Remove_duplicate_accounts(unique)
            print_blocks(blocks)
            if len(blocks) <= 0: print(f"\nx1b[93mNothing to do!\x1b[0m\n")
            print(f"\x1b[96m{file_path[file_path.find('/google.com'):]} \x1b[0m")