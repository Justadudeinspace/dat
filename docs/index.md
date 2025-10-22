---
layout: default
title: DAT · Dev Audit Tool

---

# DAT — Dev Audit Tool
<p class="lead">Compile an entire repo to a single <strong>Markdown/TXT/PDF</strong> artifact, or browse it live in the terminal. Cross-platform. Fast. Space-age.</p>

<div class="card">
  <p><strong>Install quickstart</strong></p>
  <pre><code>git clone https://github.com/Justadudeinspace/dat.git
cd dat
chmod +x install_deps.sh
./install_deps.sh
python3 dat</code></pre>
  <p>
    <a class="btn" href="{{ site.repo_url }}">View on GitHub</a>
    <a class="btn ghost" href="{{ site.baseurl }}/usage">Usage</a>
  </p>
</div>

## Highlights
- **Single file resolve**: <code>dat -s dat_pdf</code>
- **Ignore** junk: <code>-i .pyc __pycache__ .git node_modules</code>
- **Export PDF**: <code>-o repo.pdf</code>
- **Filter**: <code>-c</code> (code), <code>-d</code> (docs), <code>-m</code> (media), <code>-e py,js,md</code>
- **Summaries**: top by lines & size

## Favorite commands
```bash
dat -o repo.pdf
dat -c -i .pyc __pycache__ -o code.md
dat dat_pdf -o dat_pdf.pdf
```

---
