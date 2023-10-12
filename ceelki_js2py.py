import re

def read_lines(file):
  """Reads the lines of a file and returns them as a list."""
  with open(file, "r") as f:
    return f.read().splitlines()

def split_blocks(content):
  """Splits the content of a file into blocks, where each block is defined by a start and end marker."""
  blocks = []
  start_marker = re.compile(r"exemption: {")
  end_marker = re.compile(r"}")

  iterators = []
  for i, line in enumerate(content):
    if start_marker.match(line):
      s_index = i
    elif end_marker.match(line):
      e_index = i
      iterators.append((s_index, e_index))

  for s_index, e_index in iterators:
    block = content[s_index:e_index+1]
    blocks.append(block)

  return blocks

def sort_blocks(blocks):
  """Sorts the blocks of a file by their content."""
  blocks.sort()
  return blocks

def extract_accounts(blocks):
  """Extracts the account numbers from the blocks of a file."""
  accounts = []

  for block in blocks:
    for line in block:
      if "account: " in line:
        account = line.split("account: ")[1]
        accounts.append(account)

  return accounts

def remove_duplicates(blocks):
  """Removes duplicate blocks from a list of blocks."""
  unique_blocks = []

  for i, block in enumerate(blocks):
    if i == 0:
      unique_blocks.append(block)
    else:
      if blocks[i-1] != block:
        unique_blocks.append(block)

  return unique_blocks

def print_blocks(blocks):
  """Prints the blocks of a file to the console."""

  print("\n")
  print('\x1b[96m ------------------------------  IAM-AP CONSOLIDATION  ------------------------------- \x1b[0m')

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