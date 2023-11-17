import subprocess
from enum import Enum

cl = input("Enter the CL number: ")
command = f'g4 list -s {cl} | cut -c16- | awk \'{{cmd="p4 g4d {cl}"; cmd | getline output; close(cmd); print output $0}}\''
output = subprocess.check_output(command, shell=True, text=True)
files = output.strip().split('\n')


#class TLF(Enum):
#    bets = auto(),
#    untrusted = auto(),
#    community = auto(),
#    corp = auto(),
#    experimental = auto(),
#    legacy = auto(),
#    monitoring = auto(),
#    products = auto(),
#    teams = auto(),
#    tenancy_units = auto(),


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

if __name__ == "__main__":
    read_files()
    print_roles()
    print_accounts()
    print_wildcards()

    output = subprocess.check_output([
        "python3", "IAP_Conso.py"   
    ])

    result = output.split(b'\n')[1:-1]
    for line in result:
        print(line.decode('utf-8'))