# Homebrew formula for `flow` — a single-file, zero-dependency terminal focus app.
#
# Distributed via a personal tap, so users install with:
#   brew install thepathless/flow/flow
#
# To set up the tap (one time):
#   1. Create a GitHub repo named `homebrew-flow`.
#   2. Put this file at `Formula/flow.rb` in it.
#   3. After pushing a `vX.Y.Z` tag to the flow repo, update `url` + `sha256`
#      below (get the hash with: `curl -fsSL <url> | shasum -a 256`).

class Flow < Formula
  desc "Mouse-first terminal focus app: Pomodoro, todos, habits, ambient audio, app blocker"
  homepage "https://github.com/thepathless/flow"
  url "https://github.com/thepathless/flow/archive/refs/tags/v1.0.0.tar.gz"
  sha256 "17e071c2820f164ddff36a84022941b2705fa37fd9b787f753967eb02b98f69d"
  license "MIT"

  depends_on "python@3.12"

  def install
    bin.install "flow"
  end

  test do
    system Formula["python@3.12"].opt_bin/"python3.12", "-m", "py_compile", bin/"flow"
  end
end
