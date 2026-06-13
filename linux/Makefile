# flow — universal Linux installer.
#
#   sudo make install      install flow + desktop entry + icon system-wide
#   make install PREFIX=~/.local   per-user install (no root)
#   sudo make uninstall    remove everything this Makefile installed
#
# Works on any distribution — it just copies the single `flow` script and a
# .desktop launcher into standard locations. No build step, no dependencies.

PREFIX  ?= /usr/local
DESTDIR ?=
BINDIR   = $(DESTDIR)$(PREFIX)/bin
DATADIR  = $(DESTDIR)$(PREFIX)/share
APPDIR   = $(DATADIR)/applications
ICONDIR  = $(DATADIR)/icons/hicolor/scalable/apps

# The script lives one directory up from linux/.
SRC = ../flow

.PHONY: install uninstall

install:
	@echo "Installing flow → $(BINDIR)/flow"
	install -Dm755 $(SRC) $(BINDIR)/flow
	install -Dm644 flow.desktop $(APPDIR)/flow.desktop
	install -Dm644 flow.svg $(ICONDIR)/flow.svg
	@# Bundle the optional ambient recording next to nothing useful for PATH,
	@# so instead seed it into the invoking user's config if present.
	@mp3=$$(ls ../krishna*.mp3 2>/dev/null | head -1); \
	if [ -n "$$mp3" ]; then \
	  home=$${SUDO_USER:+$$(eval echo ~$$SUDO_USER)}; home=$${home:-$$HOME}; \
	  dst="$$home/.config/flow/sounds"; mkdir -p "$$dst"; \
	  cp -n "$$mp3" "$$dst/krishna_flute.mp3" 2>/dev/null && \
	  echo "Seeded ambient track → $$dst/krishna_flute.mp3" || true; \
	fi
	@command -v update-desktop-database >/dev/null 2>&1 && \
	  update-desktop-database "$(APPDIR)" 2>/dev/null || true
	@echo "Done. Run 'flow'."

uninstall:
	rm -f $(BINDIR)/flow
	rm -f $(APPDIR)/flow.desktop
	rm -f $(ICONDIR)/flow.svg
	@echo "Removed flow. Your data in ~/.config/flow was left untouched."
