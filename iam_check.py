#!/usr/bin/env python3
"""
IAM Check Tool - Unified script for IAM policy analysis and consolidation.

This tool scans IAM configuration files for roles, accounts, and wildcards,
and consolidates duplicate exemption blocks in iam_allowed_policy.textproto files.

Usage:
    python iam_check.py --cl <CL_NUMBER>      # Scan files in a changelist
    python iam_check.py --file <FILE_PATH>    # Analyze a specific file
    python iam_check.py --test                # Run against local pylog test file
"""

import argparse
import subprocess
import sys
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional


# =============================================================================
# ANSI Color Codes
# =============================================================================
class Color:
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    END = "\033[0m"

    @staticmethod
    def cyan(text: str) -> str:
        return f"{Color.CYAN}{text}{Color.END}"

    @staticmethod
    def green(text: str) -> str:
        return f"{Color.GREEN}{text}{Color.END}"

    @staticmethod
    def yellow(text: str) -> str:
        return f"{Color.YELLOW}{text}{Color.END}"

    @staticmethod
    def red(text: str) -> str:
        return f"{Color.RED}{text}{Color.END}"

    @staticmethod
    def header(text: str) -> str:
        padding = (80 - len(text)) // 2
        return f"{Color.CYAN}{'-' * padding} {text} {'-' * padding}{Color.END}"


# =============================================================================
# Keywords Configuration
# =============================================================================
class Keywords:
    """Central configuration for all keyword patterns."""
    ROLES = [
        "setIamPolicy",
        "roles/owner",
        "roles/editor", 
        "roles/viewer",
        "iam.serviceAccounts.actAs"
    ]
    ACCOUNTS = ["mdb:", "user:", "@google.com"]
    FILES = ["iam_allowed_policy.textproto", "iam_policy.yaml", "project.yaml"]
    WILDCARDS = [".*", "/*", "*."]


# =============================================================================
# Data Classes
# =============================================================================
@dataclass
class Finding:
    """Represents a finding (role, account, or wildcard) at a specific line."""
    line_number: int
    value: str
    file_path: str = ""


@dataclass
class CheckResults:
    """Container for all scan results."""
    roles: dict = field(default_factory=dict)
    accounts: dict = field(default_factory=dict)
    wildcards: dict = field(default_factory=dict)


# =============================================================================
# File Retrieval
# =============================================================================
def get_files_from_cl(cl_number: str) -> list[str]:
    """Retrieve file paths from a changelist using g4/p4 commands."""
    command = (
        f'g4 list -s {cl_number} | cut -c16- | '
        f'awk \'{{cmd="p4 g4d {cl_number}"; cmd | getline output; close(cmd); print output $0}}\''
    )
    try:
        output = subprocess.check_output(command, shell=True, text=True)
        files = [f for f in output.strip().split('\n') if f]
        return files
    except subprocess.CalledProcessError as e:
        print(Color.red(f"Error running g4/p4 command: {e}"))
        print(Color.yellow("Make sure you have g4/p4 tools available in your PATH."))
        return []
    except FileNotFoundError:
        print(Color.red("g4/p4 commands not found. Are you in a Google environment?"))
        return []


def get_display_path(file_path: str) -> str:
    """Extract a displayable path from a full file path."""
    if '/google.com' in file_path:
        return file_path[file_path.find('/google.com'):]
    return file_path


# =============================================================================
# File Scanning
# =============================================================================
def scan_files(file_paths: list[str], results: CheckResults) -> None:
    """Scan files for roles, accounts, and wildcards."""
    if not file_paths:
        return

    print(Color.header("FILES"))
    
    for file_path in file_paths:
        # Display file info
        found_file = [f for f in Keywords.FILES if f in file_path]
        if found_file:
            display_path = get_display_path(file_path)
            idx = display_path.find(found_file[0])
            print(f"{display_path[:idx]}{Color.cyan(found_file[0])}")
        else:
            print(Color.yellow(f"Unrecognized file type: {get_display_path(file_path)}"))

    print()

    # Scan each file
    for file_path in file_paths:
        try:
            with open(file_path, "r") as file:
                lines = file.read().split('\n')

            for line_number, line in enumerate(lines, start=1):
                # Skip comments
                if '#' in line:
                    continue

                # Check for roles
                if any(role in line for role in Keywords.ROLES):
                    if file_path not in results.roles:
                        results.roles[file_path] = []
                    results.roles[file_path].append(Finding(line_number, line, file_path))

                # Check for accounts
                if any(account in line for account in Keywords.ACCOUNTS):
                    if file_path not in results.accounts:
                        results.accounts[file_path] = []
                    results.accounts[file_path].append(Finding(line_number, line, file_path))

                # Check for wildcards
                if any(wildcard in line for wildcard in Keywords.WILDCARDS):
                    if file_path not in results.wildcards:
                        results.wildcards[file_path] = []
                    results.wildcards[file_path].append(Finding(line_number, line, file_path))

        except FileNotFoundError:
            print(Color.red(f"File not found: {get_display_path(file_path)}"))
        except IOError as e:
            print(Color.red(f"Error reading file: {get_display_path(file_path)} - {e}"))


def print_findings(results: CheckResults) -> None:
    """Print all findings (roles, accounts, wildcards)."""
    # Print roles
    if results.roles:
        print(Color.header("ROLES"))
        for file_path, findings in results.roles.items():
            print(f"{Color.green('Permissions found in:')} {get_display_path(file_path)}")
            for f in findings:
                print(f"  {Color.yellow(f'Line {f.line_number}:')} {Color.red(f.value.strip())}")
        print()

    # Print accounts
    if results.accounts:
        print(Color.header("ACCOUNTS & GROUPS"))
        for file_path, findings in results.accounts.items():
            print(f"{Color.green('Accounts found in:')} {get_display_path(file_path)}")
            for f in findings:
                print(f"  {Color.yellow(f'Line {f.line_number}:')} {Color.red(f.value.strip())}")
        print()

    # Print wildcards
    if results.wildcards:
        print(Color.header("WILDCARDS"))
        for file_path, findings in results.wildcards.items():
            print(f"{Color.green('Wildcards found in:')} {get_display_path(file_path)}")
            for f in findings:
                print(f"  {Color.yellow(f'Line {f.line_number}:')} {Color.red(f.value.strip())}")
        print()


# =============================================================================
# IAP Consolidation
# =============================================================================
def read_lines(file_path: str) -> list[str]:
    """Read a file and return its lines."""
    with open(file_path, 'r') as f:
        return f.read().splitlines()


def split_blocks(content: list[str]) -> list[list[str]]:
    """Split content into exemption blocks with their indices."""
    blocks = []
    iterators = []
    
    s_index, e_index = None, None
    sub_s_index, sub_e_index = None, None
    subblock_flag = False
    exemption_flag = False

    for index, line in enumerate(content):
        if 'exemption' in line and not exemption_flag:
            s_index = index
            exemption_flag = True
        elif 'TODO' in line:
            s_index = index
            exemption_flag = True
        elif '#' in line and 'TODO' not in line:
            continue
        elif '}' in line:
            if subblock_flag:
                sub_e_index = index
                subblock_flag = False
            elif not subblock_flag and exemption_flag:
                exemption_flag = False
                e_index = index
                iterators.append({
                    's_index': s_index,
                    'e_index': e_index,
                    'sub_s_index': sub_s_index,
                    'sub_e_index': sub_e_index
                })
        else:
            if 'conditional_account' in line:
                sub_s_index = index
                subblock_flag = True

    # Extract block contents
    for it in iterators:
        segment = []
        for i in range(it['s_index'], it['e_index'] + 1):
            segment.append(content[i])
        blocks.append(segment)

    return blocks


def extract_accounts(blocks: list[list[str]]) -> list[str]:
    """Extract account lines from blocks (modifies blocks in place)."""
    accounts = []
    
    for block in blocks:
        for line in block[:]:  # Iterate over copy
            if 'account: ' in line:
                acc_pos = block.index(line)
                block.pop(acc_pos)
                accounts.append(line)
    
    # Ensure accounts list matches blocks length
    while len(accounts) < len(blocks):
        accounts.append('')
    
    return accounts


def remove_duplicates(blocks: list[list[str]], accounts: list[str]) -> list[list[str]]:
    """Remove duplicate exemption blocks, merging their accounts."""
    if not blocks:
        return []
    
    unique = []

    for i, block in enumerate(blocks[:-1]):
        if blocks[i] == blocks[i + 1]:
            # Duplicate block found
            if not unique:
                blocks[i].insert(-2, accounts[i])
                unique.append(blocks[i])
            else:
                # Add account to existing unique block
                if len(unique) == 1:
                    unique[-1].insert(-3, accounts[i])
                else:
                    unique[-1].insert(-3, accounts[i + 1])
        else:
            # Not a duplicate - check if previous was duplicate
            if i > 0 and blocks[i] == blocks[i - 1]:
                if not any(accounts[i] in a for a in unique[-1]):
                    unique[-1].insert(-3, accounts[i])
            
            # Add current block as new unique
            tmp = blocks[i + 1][:]
            tmp.insert(-2, accounts[i + 1])
            unique.append(tmp)

    # Handle first block if unique
    if not unique or (blocks and unique and blocks[0] != unique[0][:len(blocks[0])]):
        first_block = blocks[0][:]
        first_block.insert(-2, accounts[0])
        unique.insert(0, first_block)

    return unique


def sort_lines_in_blocks(blocks: list[list[str]]) -> list[list[str]]:
    """Sort lines within each block for consistent formatting."""
    for i in range(len(blocks)):
        if len(blocks[i]) < 2:
            continue
            
        # Separate braces
        opening_brace = blocks[i].pop(0)
        closing_brace = blocks[i].pop(-1)

        # Categorize lines
        exemptions = [l for l in blocks[i] if l.strip().startswith('exemption')]
        todos = [l for l in blocks[i] if l.strip().startswith('# TODO')]
        headers = todos + exemptions

        permissions = [l for l in blocks[i] if l.strip().startswith('permission')]
        roles = [l for l in blocks[i] if l.strip().startswith('role')]
        accounts = [l for l in blocks[i] if l.strip().startswith('account:')]
        scopes = [l for l in blocks[i] if l.strip().startswith('scope')]
        
        conditionals = [l for l in blocks[i] if l.strip().startswith('conditional_account')]
        account_props = [l for l in blocks[i] if l.strip().startswith('account_property')]
        account_types = [l for l in blocks[i] if l.strip().startswith('account_type')]
        subblocks = conditionals + account_props + account_types

        # Sort
        permissions.sort()
        accounts.sort(key=lambda x: x.lower())

        # Reconstruct block
        blocks[i] = headers + permissions + roles + accounts + scopes + subblocks
        blocks[i].insert(0, opening_brace)
        
        if subblocks:
            blocks[i].append('  }')
        blocks[i].append(closing_brace)

    return blocks


def print_consolidated_blocks(blocks: list[list[str]], file_path: str = "") -> None:
    """Print consolidated exemption blocks with color coding."""
    print()
    print(Color.header("IAP CONSOLIDATION"))

    if not blocks:
        print(Color.yellow("Nothing to consolidate!"))
        return

    color_map = {
        "exemption": Color.RED,
        "conditional_account": Color.RED,
        "}": Color.RED,
        "account": Color.YELLOW,
        "scope": Color.CYAN,
        "# TODO": Color.GREEN,
    }

    for block in blocks:
        for line in block:
            color = Color.END
            for keyword, col in color_map.items():
                if keyword in line:
                    color = col
                    break
            print(f"{color}{line}{Color.END}")
        print()

    if file_path:
        print(Color.cyan(get_display_path(file_path)))


def consolidate_file(file_path: str) -> None:
    """Run consolidation on a single iam_allowed_policy.textproto file."""
    content = read_lines(file_path)
    blocks = split_blocks(content)
    blocks.sort()

    accounts = extract_accounts(blocks)
    blocks = remove_duplicates(blocks, accounts)
    blocks = sort_lines_in_blocks(blocks)

    print_consolidated_blocks(blocks, file_path)


# =============================================================================
# Main Entry Point
# =============================================================================
def main():
    parser = argparse.ArgumentParser(
        description="IAM Check Tool - Analyze and consolidate IAM policy files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python iam_check.py --cl 123456        # Scan files in changelist 123456
  python iam_check.py --file policy.txt  # Analyze a specific file
  python iam_check.py --test             # Run against local pylog test file
        """
    )
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--cl', type=str, help='Changelist number to scan')
    group.add_argument('--file', type=str, help='Path to a file to analyze')
    group.add_argument('--test', action='store_true', help='Run against local pylog test file')
    
    parser.add_argument('--no-consolidate', action='store_true', 
                        help='Skip consolidation step (scan only)')

    args = parser.parse_args()

    results = CheckResults()

    if args.cl:
        # CL mode - scan files from changelist
        files = get_files_from_cl(args.cl)
        if not files:
            print(Color.red("No files found in changelist."))
            sys.exit(1)
        
        scan_files(files, results)
        print_findings(results)

        # Run consolidation on any iam_allowed_policy.textproto files
        if not args.no_consolidate:
            for file_path in files:
                if "iam_allowed_policy.textproto" in file_path:
                    consolidate_file(file_path)

    elif args.file:
        # Single file mode
        file_path = args.file
        if not Path(file_path).exists():
            print(Color.red(f"File not found: {file_path}"))
            sys.exit(1)

        if "iam_allowed_policy.textproto" in file_path or file_path.endswith('.textproto'):
            consolidate_file(file_path)
        else:
            scan_files([file_path], results)
            print_findings(results)

    elif args.test:
        # Test mode - use local pylog file
        script_dir = Path(__file__).parent
        pylog_path = script_dir / "pylog"
        
        if not pylog_path.exists():
            print(Color.red(f"Test file not found: {pylog_path}"))
            sys.exit(1)

        print(Color.green(f"Running test with: {pylog_path}"))
        print()
        consolidate_file(str(pylog_path))


if __name__ == "__main__":
    main()
