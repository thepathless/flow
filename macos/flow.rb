# Homebrew formula for flow — a single-file terminal focus app.
#
# Works on macOS and Linux (Linuxbrew). flow has no Python dependencies; we only
# depend on a Python 3 interpreter to run it.
#
# Before publishing: set the real `url` tag and fill `sha256` (see macos/README.md).
# Before publishing: set the real `url` tag and fill `sha256` (see macos/README.md).
require "language/python"

class FlowTui < Formula
  include Language::Python::Shebang

  desc "Mouse-first terminal focus app: Pomodoro, todos, habits, ambient audio, app blocker"
  homepage "https://github.com/thepathless/flow"
  url "https://github.com/thepathless/flow/archive/refs/tags/v1.0.0.tar.gz"
  sha256 "REPLACE_WITH_TARBALL_SHA256"
  license "MIT"
  head "https://github.com/thepathless/flow.git", branch: "main"

  depends_on "python@3.12"

  # Optional features light up automatically when these are installed:
  #   brew install mpv cava   # audio + visualizer
  uses_from_macos "ncurses"

  def install
    bin.install "flow"
    # Pin flow's shebang to this formula's Python so it runs against a known-good
    # interpreter regardless of the user's PATH.
    rewrite_shebang detected_python_shebang(self), bin/"flow"
  end

  test do
    # flow is a curses TUI; just confirm it's installed and byte-compiles cleanly.
    assert_path_exists bin/"flow"
    system Formula["python@3.12"].opt_bin/"python3.12", "-m", "py_compile", bin/"flow"
  end
end
