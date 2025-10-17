### 🧩 `docs/INSTALLATION.md`

# Installation Guide

`dat` supports Linux, macOS, Windows, and Termux (Android).

---

## Step 1: Clone the Repository
```bash
git clone https://github.com/Justadudeinspace/dat.git
cd dat
```

---

Step 2: Install Requirements
```
pip install -r requirements.txt
```
Optional:
```
pip install colorama Pillow PyPDF2
```

---

Step 3: Run the Bootstrap Script
```
chmod +x bootstrap.sh
./bootstrap.sh
```
This will:

Create a virtual environment

Install dependencies

Create the dat shim

Prepare for global usage



---

Step 4: Verify Installation

./dat --version

Expected output:

dat v1.0.0 (Python 3.x)
Platform: Linux/Termux/macOS/Windows

---
