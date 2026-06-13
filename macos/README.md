# macOS

`flow` is a single Python script, so on macOS there is nothing to compile. Two
ways to install — pick one.

## Option A — pip (simplest, no setup)

macOS ships Python 3 (or install it with `brew install python`). Then:

```sh
pip3 install flow-tui
flow
```

That's it. Run `flow` inside **Terminal.app** or **iTerm2**.

## Option B — Homebrew

Once published to a tap, users get:

```sh
brew install <your-username>/flow/flow-tui
```

### Publishing the formula (one-time)

The formula is [`flow.rb`](flow.rb). Homebrew serves formulae from a "tap" repo
named `homebrew-<something>`.

1. Tag a release on GitHub (e.g. `v1.0.0`) so the source tarball URL exists.
2. Compute its checksum and paste it into `flow.rb` (`sha256`):
   ```sh
   curl -fsSL https://github.com/<your-username>/flow/archive/refs/tags/v1.0.0.tar.gz | shasum -a 256
   ```
3. Create a second GitHub repo named **`homebrew-flow`** and add `flow.rb` to it.
4. Users then run:
   ```sh
   brew tap <your-username>/flow            # adds github.com/<your-username>/homebrew-flow
   brew install flow-tui
   ```

### Try the formula locally before publishing

```sh
brew install --build-from-source ./macos/flow.rb
brew test flow-tui
brew audit --new flow-tui      # lint before submitting
```

> Homebrew works on Linux too (Linuxbrew) — the same formula installs there.

## Optional features

`brew install mpv cava` enables audio playback and the audio-reactive
visualizer. Everything else works without them.
