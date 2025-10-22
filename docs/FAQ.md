---
layout: page
title: FAQ

---

**`-s` says “unrecognized”.**  
Likely an older `dat` on your PATH. Run `python3 ./dat --no-bootstrap --version` in the repo. Reinstall to `~/.local/bin` if needed.

**PDF shows black squares.**  
Install DejaVu Sans Mono (auto-installed where supported). DAT sanitizes box drawing if the font isn’t available.

**Ignore junk?**  
`dat -i .pyc __pycache__ .git node_modules` (accepts spaces or commas).

**Where does DAT install?**  
Defaults to a user bin (Linux/macOS) or a Termux/Windows path. Use `--no-bootstrap` to skip.


---
