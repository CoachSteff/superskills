# v2.2.1 GitHub Push Instructions

## Push Commands

Execute these commands in order:

```bash
# 1. Push commits to master branch
git push origin master

# 2. Push the v2.2.1 tag
git push origin v2.2.1

# 3. Verify the push was successful
git status
git ls-remote --tags origin | grep v2.2
```

## Expected Results

### After Step 1 (Push commits)
```
Enumerating objects: 20, done.
Counting objects: 100% (20/20), done.
Delta compression using up to 8 threads
Compressing objects: 100% (12/12), done.
Writing objects: 100% (12/12), X KiB | X MiB/s, done.
Total 12 (delta 8), reused 0 (delta 0)
To github.com:CoachSteff/superskills.git
   98a544d..ae7f216  master -> master
```

### After Step 2 (Push tag)
```
Enumerating objects: 1, done.
Counting objects: 100% (1/1), done.
Writing objects: 100% (1/1), 186 bytes | 186.00 KiB/s, done.
Total 1 (delta 0), reused 0 (delta 0)
To github.com:CoachSteff/superskills.git
 * [new tag]         v2.2.1 -> v2.2.1
```

### After Step 3 (Verify)
```
On branch master
Your branch is up to date with 'origin/master'.

nothing to commit, working tree clean

c96c515aa19b02423adc9aa9bd9e603a51e4574c	refs/tags/v2.2.1
```

## Next: Create GitHub Release

Once push is complete, create the GitHub release:

1. **Navigate to:** https://github.com/CoachSteff/superskills/releases/new

2. **Choose tag:** `v2.2.1` (from dropdown)

3. **Release title:** `v2.2.1 - Critical Patch Release`

4. **Description:** Copy the entire content from:
   ```bash
   cat dev/GITHUB_RELEASE_v2.2.1.md
   ```

5. **Settings:**
   - ✅ Set as the latest release
   - ❌ DO NOT mark as pre-release

6. **Click:** "Publish release"

## Verification Checklist

After release is published:

- [ ] Visit: https://github.com/CoachSteff/superskills/releases
- [ ] Confirm v2.2.1 shows as "Latest"
- [ ] Confirm tag v2.2.1 is visible
- [ ] Test install: `pipx install superskills`
- [ ] Test upgrade: `pipx upgrade superskills`
- [ ] Verify version: `superskills --version` → `2.2.1`

## GitHub Release Description Preview

The release description is ready in: `dev/GITHUB_RELEASE_v2.2.1.md`

It includes:
- 🚨 Critical patch notice
- 4 detailed fix descriptions with before/after examples
- Installation and upgrade instructions
- Post-upgrade verification steps
- Complete testing summary
- Migration notes (no action required)
- Support links

---

**Status:** Ready to push
**Action Required:** Execute the 3 bash commands above
