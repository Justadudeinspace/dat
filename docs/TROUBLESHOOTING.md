🧰 docs/TROUBLESHOOTING.md

# Troubleshooting

### ❌ Command Not Found
Run:
```bash
chmod +x dat
```
Or:
```
python dat.py
```
❌ Missing Dependencies

Install via:
````
pip install -r requirements.txt
```
⚠️ Bootstrap Fails

Ensure you have python3-venv or libmagic installed:
```
sudo apt install python3-venv libmagic-dev
```
🪲 No Output or Empty Audit

Check file filters. Example:
```
dat -a -c
```
To disable filters:
```
dat
```
