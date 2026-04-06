# Git Quick Reference — Neural Speed Academy

Practical commands for pulling changes, switching branches, and fixing common issues.

## Daily Workflow

### Pull latest changes
```bash
git pull
python nsa.py
```

### Check what branch you're on
```bash
git branch
```

### Switch to a feature branch
```bash
git checkout feature/pacer-improvements
git pull
```

### Check recent commits (verify you have the latest)
```bash
git log --oneline -5
```

## When Things Look Wrong

### Changes not showing up after pull
Python caches compiled files. Delete them:
```bash
rmdir /s /q neural_speed_academy\__pycache__
rmdir /s /q neural_speed_academy\exercises\__pycache__
rmdir /s /q neural_speed_academy\screens\__pycache__
python nsa.py
```

Or skip cache entirely:
```bash
python -B nsa.py
```

### Force your branch to match the remote exactly
Use when your local branch has stale or extra commits:
```bash
git fetch origin
git reset --hard origin/feature/pacer-improvements
python nsa.py
```
Replace `feature/pacer-improvements` with your branch name.

### Check if a specific change is in your files
```bash
findstr "ultra" neural_speed_academy\theme.py
```

### Verify a module loads correctly
```bash
python -c "from neural_speed_academy.theme import FOV_PRESETS; print(list(FOV_PRESETS.keys()))"
```

## Branch Management

### See all branches
```bash
git branch
```

### Pull a branch after rebase/merge to main
```bash
git checkout feature/pacer-improvements
git pull origin main
```

### Remove an extra commit that shouldn't be on your branch
```bash
git reset --hard origin/feature/pacer-improvements
```

### Check what's different between your branch and remote
```bash
git log --oneline origin/feature/pacer-improvements..HEAD
```
Empty output = you're in sync.

## Troubleshooting Checklist

1. **Can't see changes?**
   - Run `git log --oneline -3` — do you see the expected commit?
   - If no: `git pull`
   - If yes: delete `__pycache__` directories, then restart

2. **Pull gives warnings about skipped commits?**
   - Normal after a rebase. The pull succeeded.

3. **Pull fails with conflicts?**
   - `git fetch origin && git reset --hard origin/<branch-name>`
   - This discards local changes and matches the remote exactly.

4. **Wrong branch?**
   - `git branch` to check
   - `git checkout <correct-branch>` to switch
