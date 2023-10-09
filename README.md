1. Read pylog contents, regex for all the exemption blocks, store them and index them (exemption_block 1, 2, 3, etc.)
2. Iterate through exemption_blocks identifying sets of duplicate permissions between them
3. Flag the blocks (by index number) that contain duplicate perms as "duplicated_blocks" copy them to a separate var and index them
4. Copy identities so strings that start after the last listed permission and before block's } in each of the "duplicated_blocks", paste all that under the last permission in the lowest indexed block flagged as duplicated_blocks
5. Remove the remaining (index higher than the lowest number) sets of blocks that were flagged containing duplicate permissions
