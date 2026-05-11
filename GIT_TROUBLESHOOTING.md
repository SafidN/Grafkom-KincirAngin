# 🔧 Git Push Troubleshooting Guide

## ❌ Error: "rejected" saat git push

### Skenario 1: Remote has changes you don't have locally

**Error Message:**
```
! [rejected]        main -> main (fetch first)
error: failed to push some refs to 'https://github.com/SafidN/Grafkom-KincirAngin.git'
hint: Updates were rejected because the remote contains work that you do not have locally.
```

**Penyebab:** Ada commit di GitHub yang belum ada di local Anda.

**Solusi:**

#### Option A: Pull dengan Merge (Recommended)
```bash
git pull origin main
git push origin main
```

#### Option B: Pull dengan Rebase (Cleaner history)
```bash
git pull origin main --rebase
git push origin main
```

---

### Skenario 2: Non-fast-forward

**Error Message:**
```
! [rejected]        main -> main (non-fast-forward)
error: failed to push some refs to 'https://github.com/SafidN/Grafkom-KincirAngin.git'
hint: Updates were rejected because the tip of your current branch is behind
```

**Penyebab:** History di remote berbeda dengan local.

**Solusi:**

#### Step 1: Fetch remote changes
```bash
git fetch origin
```

#### Step 2: Merge atau Rebase
```bash
# Option A: Merge
git merge origin/main

# Option B: Rebase (cleaner)
git rebase origin/main
```

#### Step 3: Push
```bash
git push origin main
```

---

### Skenario 3: Force Push Needed (HATI-HATI!)

**Warning:** ⚠️ Force push akan menghapus history di remote!

**Hanya gunakan jika:**
- Anda yakin ingin menimpa remote
- Tidak ada orang lain yang bekerja di repository
- Anda sudah backup

**Command:**
```bash
# Force push (DANGEROUS!)
git push origin main --force

# Safer force push (checks remote first)
git push origin main --force-with-lease
```

---

### Skenario 4: Authentication Error

**Error Message:**
```
remote: Permission denied
fatal: Authentication failed
```

**Penyebab:** Credential tidak valid atau expired.

**Solusi:**

#### Windows (Credential Manager)
```bash
# Clear credentials
git credential-manager-core erase

# Or update remote URL with token
git remote set-url origin https://YOUR_TOKEN@github.com/SafidN/Grafkom-KincirAngin.git
```

#### Generate Personal Access Token
1. Go to GitHub → Settings → Developer settings
2. Personal access tokens → Tokens (classic)
3. Generate new token
4. Select scopes: `repo` (full control)
5. Copy token
6. Use token as password when pushing

---

### Skenario 5: Large File Error

**Error Message:**
```
remote: error: File xxx is 100.00 MB; this exceeds GitHub's file size limit of 100 MB
```

**Solusi:**

#### Remove large file from history
```bash
# Find large files
git rev-list --objects --all | grep "$(git verify-pack -v .git/objects/pack/*.idx | sort -k 3 -n | tail -10 | awk '{print$1}')"

# Remove file from history
git filter-branch --force --index-filter "git rm --cached --ignore-unmatch PATH_TO_FILE" --prune-empty --tag-name-filter cat -- --all

# Force push
git push origin main --force
```

---

## 🛠️ Common Git Commands

### Check Status
```bash
git status
```

### View Commit History
```bash
git log --oneline -10
```

### View Remote URL
```bash
git remote -v
```

### View Differences
```bash
# Uncommitted changes
git diff

# Staged changes
git diff --staged

# Compare with remote
git diff origin/main
```

### Undo Changes

#### Undo uncommitted changes
```bash
# Single file
git checkout -- filename

# All files
git checkout -- .
```

#### Undo last commit (keep changes)
```bash
git reset --soft HEAD~1
```

#### Undo last commit (discard changes)
```bash
git reset --hard HEAD~1
```

---

## 📋 Step-by-Step Push Workflow

### Normal Push (No Errors)
```bash
# 1. Check status
git status

# 2. Add files
git add .

# 3. Commit
git commit -m "Your commit message"

# 4. Push
git push origin main
```

### Push with Potential Conflicts
```bash
# 1. Check status
git status

# 2. Add files
git add .

# 3. Commit
git commit -m "Your commit message"

# 4. Pull first (to get remote changes)
git pull origin main

# 5. Resolve conflicts if any
# Edit conflicted files, then:
git add .
git commit -m "Resolve conflicts"

# 6. Push
git push origin main
```

---

## 🔍 Diagnostic Commands

### Check if you're ahead/behind remote
```bash
git status -sb
```

### View remote branches
```bash
git branch -r
```

### View all branches
```bash
git branch -a
```

### Check remote connection
```bash
git remote show origin
```

### Verify repository URL
```bash
git config --get remote.origin.url
```

---

## 🚨 Emergency Recovery

### If you messed up and need to reset to remote
```bash
# WARNING: This will discard ALL local changes!
git fetch origin
git reset --hard origin/main
```

### If you need to save local changes first
```bash
# Save changes to stash
git stash

# Reset to remote
git fetch origin
git reset --hard origin/main

# Restore your changes
git stash pop
```

---

## 💡 Best Practices

### Before Pushing
1. ✅ Always `git pull` before `git push`
2. ✅ Check `git status` to see what you're committing
3. ✅ Write clear commit messages
4. ✅ Test your code before committing

### Commit Messages
```bash
# Good
git commit -m "Add wolf patrol animation with 4 movement types"

# Bad
git commit -m "update"
```

### Branch Strategy
```bash
# Create feature branch
git checkout -b feature/new-feature

# Work on feature
git add .
git commit -m "Add new feature"

# Push feature branch
git push origin feature/new-feature

# Merge to main (on GitHub via Pull Request)
```

---

## 🆘 Quick Fix Commands

### Forgot to pull before commit
```bash
git pull origin main --rebase
git push origin main
```

### Committed to wrong branch
```bash
# Save commit
git log  # copy commit hash

# Switch to correct branch
git checkout correct-branch

# Cherry-pick commit
git cherry-pick COMMIT_HASH

# Push
git push origin correct-branch
```

### Want to undo last push (DANGEROUS!)
```bash
# Reset local
git reset --hard HEAD~1

# Force push (WARNING!)
git push origin main --force
```

---

## 📞 Need More Help?

### Check Git Documentation
```bash
git help push
git help pull
git help rebase
```

### Common Resources
- [Git Documentation](https://git-scm.com/doc)
- [GitHub Guides](https://guides.github.com/)
- [Atlassian Git Tutorials](https://www.atlassian.com/git/tutorials)

---

## 🎯 Your Current Repository Status

Run these commands to diagnose:

```bash
# 1. Check status
git status

# 2. Check remote
git remote -v

# 3. Check branch
git branch -a

# 4. Check log
git log --oneline -5

# 5. Check if ahead/behind
git status -sb
```

---

**Last Updated:** 2026-05-11

**Repository:** https://github.com/SafidN/Grafkom-KincirAngin
