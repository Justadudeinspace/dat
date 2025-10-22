---
layout: page
title: Usage

---

## Basics
```bash
dat                 # recurse current dir
dat /path/to/dir    # audit a specific path

Filters

dat -c              # code only
dat -d              # docs only
dat -m              # media only
dat -e py,js,md     # custom ext (also accepts .py,.js,.md)

Ignore patterns

dat -i .pyc __pycache__ .git node_modules

Output

dat -o audit.md     # markdown
dat -o audit.txt    # text
dat -o repo.pdf     # PDF

Single file (with or without extension)

dat -s dat_pdf
dat dat_pdf -o dat_pdf.md
dat dat_pdf -o dat_pdf.pdf

Limits & summary

dat --max-lines 200
dat --max-size 5242880
dat --top-n 10
```

---
