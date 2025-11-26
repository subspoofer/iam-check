IAM Check Tool - Unified script for IAM policy analysis and consolidation.

This tool scans IAM configuration files for roles, accounts, and wildcards,
and consolidates duplicate exemption blocks in iam_allowed_policy.textproto files.

Usage:
    python iam_check.py --cl <CL_NUMBER>      # Scan files in a changelist
    python iam_check.py --file <FILE_PATH>    # Analyze a specific file
    python iam_check.py --test                # Run against local pylog test file
