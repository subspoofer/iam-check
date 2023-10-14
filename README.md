IAP logic:
1. Read file contents, store them.
2. Identify all the exemption blocks, store them and index them (exemption_block 1, 2, 3, etc.).
3. Iterate through exemption_blocks identifying sets of duplicate permissions between them, each group of duplicate permissions is to be stored as indexed set so "duplicate_permissions_set1" etc.
4. Flag all the blocks (by index number) that contain duplicate permission set as "duplicate_block", copy them to a separate var and index them by the "duplicate_permissions_set1"
(so if a block contained "duplicate_permissions_set1" it is indexed "duplicate_block_set1", if set2 then "duplicate_block_set2" and so on).
5. Copy identities (and scopes) - so strings that start after the last listed permission and before block's } in each of the "duplicated_blocks", paste all that under the "duplicate_block_setX" where X is the lowest index of a given set.
6. Remove the remaining (index higher than the lowest in given set) sets of "duplicate_block" that were flagged containing duplicate permissions.


Pseudo code:
