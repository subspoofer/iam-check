Python script for neatly listing all roles, groups and accounts in GCP IAM (iam_policy.yaml) config files\
and to automatically consolidate repeated exemption blocks in auto-generated IAP (iam_allowed_policy.textproto) files.

No prereqs, assuming you use Google's customized version of Perforce ;)\
(Perforce’s binary is called `p4`, and Google’s variant is `g4`).\
Should be easy to modify if you need this to run with `p4`.
