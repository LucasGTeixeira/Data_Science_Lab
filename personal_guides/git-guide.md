# Git Guide

> A "when do I reach for this?" reference. Every section starts with the
> situation that calls for it, then the commands.

Git snapshots your project every time you commit, so you can go back in time,
work on several things at once, and collaborate without stepping on each
other. Three ideas carry you a long way: the **working directory** (files
you're editing), the **staging area** (changes picked for the next snapshot),
and **commits** (the snapshots). Branches are just movable labels pointing at
a commit.

The everyday loop covers 90% of usage:

```
edit files -> git status -> git add <files> -> git commit -m "why" -> git push
```

## Setup — once per machine

> **When:** right after installing Git, before your first commit. This is
> identity and defaults, not per-project.

```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
git config --global init.defaultBranch main
git config --list                 # show current config
```

## Starting a repo

> **When:** `init` for a brand-new project; `clone` when the project already
> exists on GitHub/GitLab and you want a local copy.

```bash
git init                          # new repo in current dir
git clone <url>                   # copy remote repo
git clone <url> myfolder          # copy into a folder name
git clone --depth 1 <url>         # shallow clone (faster, no history)
```

`--depth 1` is for when you only need the current files (deploys, inspecting
someone else's code) — not for work you'll commit to.

## The 3 areas

```
working dir  --add-->  staging  --commit-->  local repo  --push-->  remote
```

Staging is what throws beginners off. Its purpose: choose exactly what goes
into the next commit. Changed five files but only two belong to this fix?
Stage those two. That's why `add` and `commit` are separate steps.

## Everyday workflow

> **When:** the loop you repeat all day — check what changed, stage it,
> commit it, send it upstream.

```bash
git status                        # what changed (run this constantly)
git status -s                     # short form
git diff                          # unstaged changes
git diff --staged                 # staged changes
git add file.py                   # stage one file
git add .                         # stage everything
git add -p                        # stage piece by piece (review hunks)
git commit -m "message"           # commit staged
git commit -am "message"          # stage tracked + commit
git commit --amend                # edit last commit (unpushed only)
git push                          # send to remote
git pull                          # fetch + merge remote
```

Two habits worth the effort:

- `git diff --staged` before every commit — last chance to catch a stray debug
  print or an accidental `.env`.
- `git add -p` when you changed several unrelated things at once; it asks
  yes/no per hunk so one messy session becomes clean, focused commits.

## History

> **When:** you need to understand the past — what changed, when, and by whom.
> `log` for the timeline, `blame` for one suspicious line, `show` for a commit.

```bash
git log                           # full history
git log --oneline --graph --all   # compact visual (best default)
git log -p file.py                # history of a file w/ diffs
git show <hash>                   # inspect a commit
git blame file.py                 # who wrote each line
git shortlog -sn                  # commits per author
```

## Branching

> **When:** before starting any new feature, fix, or experiment. Keeping `main`
> working is the point — risky work happens on a branch and merges back only
> when it's good.

```bash
git branch                        # list local
git branch -a                     # list all (incl. remote)
git switch -c feature             # create + switch
git switch main                   # switch
git branch -d feature             # delete (safe: warns if unmerged)
git branch -D feature             # delete (force)
git branch -m newname             # rename current
git merge feature                 # merge into current
git merge --no-ff feature         # merge with merge commit (keeps branch shape)
git rebase main                   # replay current onto main
```

Merge vs rebase:

- **merge** preserves history exactly as it happened; always safe. Use it on
  shared branches.
- **rebase** replays your commits on top of newer main for a linear history.
  Neat, but never rebase a branch someone else is building on.

## Remotes

> **When:** connecting a local repo to GitHub/GitLab, or syncing with others.
> `fetch` downloads without touching your work (a safe peek); `pull` =
> `fetch` + merge.

```bash
git remote -v                     # list remotes
git remote add origin <url>       # add remote
git remote set-url origin <url>   # change url
git fetch origin                  # download, don't merge
git push -u origin main           # push + set upstream
git push origin --delete feature  # delete remote branch
```

## Undo / recover — pick by intent

> **When:** something went wrong. Find your row below. The key distinction:
> `restore`/`reset` rewrite local history (safe only before pushing), while
> `revert` adds a new commit (safe anywhere, even after pushing).

| I want to... | Command | Risk |
|---|---|---|
| discard changes in one file | `git restore file.py` | loses the edits |
| unstage a file, keep changes | `git restore --staged file.py` | none |
| undo last commit, keep content staged | `git reset --soft HEAD~1` | none |
| undo last commit, keep content in working dir | `git reset --mixed HEAD~1` | none |
| undo last commit and destroy content | `git reset --hard HEAD~1` | data loss |
| undo a commit that's already pushed | `git revert <hash>` | none |
| park work to do something else | `git stash` | none |
| recover work that looks lost | `git reflog` | none |

```bash
git restore file.py               # discard working changes
git restore --staged file.py      # unstage (keep changes)
git reset --soft HEAD~1           # undo commit, keep staged
git reset --mixed HEAD~1          # undo commit, unstage (default)
git reset --hard HEAD~1           # undo commit, DESTROY changes
git revert <hash>                 # new commit that undoes a commit
git stash                         # shelve changes
git stash pop                     # restore + drop stash
git stash list                    # see stashes
git clean -fd                     # remove untracked files/dirs (careful)
git reflog                        # every HEAD move (recover lost work)
```

`reflog` is the safety net: it records every position HEAD has been in, even
commits a hard reset appeared to delete. Think you lost work? Check here before
panicking.

## Tags & releases

> **When:** marking a point worth finding again — a release, a submission, a
> milestone. Tags are permanent labels on commits.

```bash
git tag                           # list tags
git tag v1.0.0                    # lightweight tag
git tag -a v1.0.0 -m "release"    # annotated tag (use for releases)
git push origin v1.0.0            # push a tag
git push origin --tags            # push all tags
```

## .gitignore

> **When:** at the start of a project, before your first `git add .`. Keeps
> junk (caches, logs, data files) and secrets out of history.

```gitignore
*.log           # all .log files
__pycache__/    # ignore a dir
.env            # one file
!keep.log       # re-include exception
```

Already tracked a file you now want ignored? `.gitignore` won't untrack it:

```bash
git rm --cached file.py           # stop tracking, keep on disk
```

If you ever commit a secret, deleting it later doesn't remove it from
history — the key is out. Revoke/rotate it immediately.

## Resolving conflicts

> **When:** `merge`, `rebase`, or `pull` stops with CONFLICT. Both sides edited
> the same lines and Git won't guess; you choose.

```bash
git merge feature                 # conflict markers appear
# edit files, remove <<<<<<< ======= >>>>>>>
git add <resolved>
git commit                        # finish merge
git merge --abort                 # bail out, back to before the merge
```

Between `<<<<<<<` and `=======` is your side; from `=======` to `>>>>>>>` is
the incoming side. Make the file read how you want, delete every marker line,
then add and commit. When in doubt, `--abort` and think.

## Useful recovery

> **When:** you need a specific piece of the past back, or a bug appeared "out
> of nowhere" and you want to know which commit introduced it.

```bash
git checkout <hash> -- file.py    # restore a file from a commit
git reset --hard origin/main      # match remote exactly
git bisect start                  # binary-search the commit that broke it
git commit --amend --no-edit      # add to last commit, same message
```

`bisect` marks a good and a bad commit, checks out the middle, and asks you to
judge good/bad — it narrows to the culprit in log₂(n) steps.

## Golden rules

- Commit small and often; one idea per commit.
- Never rewrite pushed history (`amend`/`rebase` on shared branches).
- Pull before you push.
- `.gitignore` before adding secrets — never commit keys. If one leaks, rotate it.
