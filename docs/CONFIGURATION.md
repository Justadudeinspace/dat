### 🧭 `docs/CONFIGURATION.md`

# Configuration

`dat` reads an optional configuration file from:

```
~/.datconfig
```
This file customizes global defaults for filtering, limits, and summary output.

---

## Example Configuration

```ini
[Settings]
top_n = 10
max_lines = 1000
max_size = 10485760  # 10 MB

[FileTypes]
doc_extensions = .md,.txt,.rst,.pdf,.docx
code_extensions = .py,.js,.cpp,.c,.sh,.rs,.java,.go
media_extensions = .jpg,.png,.mp3,.mp4,.svg

[CustomExtensions]
extensions = .foo,.bar
```

---

## Notes

Missing values revert to internal defaults.

You can override configuration at runtime using CLI flags.

The config file is human-editable and optional.

---
