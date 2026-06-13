# Uploading flow to GitHub — first-time guide

You've never used GitHub before, so this walks through it from zero. You only do
steps 1–3 once ever; after that, publishing is steps 4–6.

> The actual automation lives in [`../.github/workflows/`](../.github/workflows/)
> (GitHub requires that exact location — it can't go inside this `github/` folder).
> This file is just the how-to.

---

## 1. One-time setup

1. **Make a GitHub account:** https://github.com/signup
2. **Install git:**
   - Linux (Arch): `sudo pacman -S git`  ·  (Debian/Ubuntu): `sudo apt install git`
   - macOS: `brew install git` (or run `git` once to get the Xcode tools prompt)
   - Windows: https://git-scm.com/download/win
3. **Tell git who you are** (use your GitHub email):
   ```sh
   git config --global user.name  "Your Name"
   git config --global user.email "you@example.com"
   ```
4. **Install the GitHub CLI** (optional but makes auth + repo creation painless):
   https://cli.github.com — then `gh auth login` and follow the browser prompts.

## 2. Fill in the placeholders

A few files contain `<your-username>` / `<your name>` / `<you@example.com>`.
Replace them with your real values:

- `README.md`, `pyproject.toml`
- `linux/PKGBUILD`, `linux/nfpm.yaml`
- `macos/flow.rb`, `LICENSE`

Quick find-and-replace from the repo root (set `GH=yourname` first):

```sh
GH=yourname
grep -rl '<your-username>' . | xargs sed -i "s/<your-username>/$GH/g"
```

## 3. Create the repository

**Easiest, with the GitHub CLI** (run from the repo root, i.e. the folder containing `flow`):

```sh
git init
git add .
git commit -m "Initial commit: flow 1.0.0"
git branch -M main
gh repo create flow --public --source=. --remote=origin --push
```

That's it — your code is on GitHub.

<details>
<summary>Without the CLI (web UI)</summary>

1. Go to https://github.com/new, name it **flow**, leave it empty (no README), click *Create*.
2. Back in your terminal:
   ```sh
   git init
   git add .
   git commit -m "Initial commit: flow 1.0.0"
   git branch -M main
   git remote add origin https://github.com/<your-username>/flow.git
   git push -u origin main
   ```
   When prompted for a password, paste a **Personal Access Token**
   (github.com → Settings → Developer settings → Tokens), not your account password.
</details>

## 4. Everyday updates

After the first push, publishing changes is just:

```sh
git add -A
git commit -m "describe what changed"
git push
```

Each push runs the **CI** workflow (byte-compiles `flow`, builds the package).
Watch it under the **Actions** tab on your repo.

## 5. Cut a release (builds the AppImage automatically)

Tag a version and push the tag — the **Release** workflow then builds the
AppImage + Python wheel and publishes them on the repo's **Releases** page:

```sh
git tag v1.0.0
git push origin v1.0.0
```

A few minutes later, `flow-x86_64.AppImage` will be downloadable from
`https://github.com/<your-username>/flow/releases`. Bump the number
(`v1.0.1`, `v1.1.0`, …) for future releases, and keep `version` in
`pyproject.toml` in sync.

## 6. (Optional) Publish to package managers

Once a release/tag exists, follow the per-platform guides:

- **PyPI** (`pip install flow-tui`): `python -m build && python -m twine upload dist/*`
- **AUR** (`yay -S flow-tui`): [`../linux/README.md`](../linux/README.md#2-arch-linux--manjaro--pacman-via-the-aur)
- **Homebrew** (`brew install`): [`../macos/README.md`](../macos/README.md#publishing-the-formula-one-time)

---

### Common snags

- **`git push` asks for a password and rejects it** → GitHub no longer accepts
  account passwords over HTTPS. Use `gh auth login`, or create a Personal Access
  Token and paste that as the password.
- **Don't commit junk** → a [`.gitignore`](../.gitignore) is already included so
  `__pycache__/`, build outputs and `*.AppImage` stay out of the repo.
- **Actions tab shows a red ✗** → click the run to see logs; the CI step that
  failed (compile or build) is named so you can pinpoint it.
