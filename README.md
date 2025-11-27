# IAM Check Tool

Script for analyzing GCP IAM configuration files and consolidating duplicate exemption blocks.

## Features

- **Scan IAM files** for roles, accounts, groups, and wildcards
- **Consolidate duplicate exemption blocks** in `iam_allowed_policy.textproto` files
- **Color-coded output** for easy reading
- Works with `g4`/`p4` changelists or standalone files

## Usage

```bash
# Scan files in a changelist (requires g4/p4)
python iam_check.py --cl <CL_NUMBER>

# Analyze a specific file
python iam_check.py --file <FILE_PATH>

# Run against local test file (pylog_test.yml)
python iam_check.py --test

# Scan only, skip consolidation step
python iam_check.py --cl <CL_NUMBER> --no-consolidate
```

## What It Detects

| Category | Keywords |
|----------|----------|
| **Roles** | `setIamPolicy`, `roles/owner`, `roles/editor`, `roles/viewer`, `iam.serviceAccounts.actAs` |
| **Accounts** | `mdb:`, `user:`, `@google.com` |
| **Files** | `iam_allowed_policy.textproto`, `iam_policy.yaml`, `project.yaml` |
| **Wildcards** | `.*`, `/*`, `*.` |

## Consolidation

The tool automatically merges duplicate exemption blocks that have identical permissions, combining their accounts into a single block. This reduces redundancy in `iam_allowed_policy.textproto` files.

## Requirements

- Python 3.9+
- `g4`/`p4` tools (only needed for `--cl` mode)
