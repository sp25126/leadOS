import os
import re

def clean_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        try:
            with open(filepath, 'r', encoding='latin-1') as f:
                content = f.read()
        except: return

    content = content.replace('\u2014', '-')
    content = content.replace('\u2013', '-')
    content = content.replace('\u2192', '->')
    
    # Replace common emoji patterns if still there
    content = re.sub(r'[^\x00-\x7F]+', ' ', content)
    
    with open(filepath, 'w', encoding='ascii') as f:
        f.write(content)

for root, dirs, files in os.walk('.'):
    if '__pycache__' in dirs: dirs.remove('__pycache__')
    if 'venv' in dirs: dirs.remove('venv')
    for name in files:
        if name.endswith('.py'):
            clean_file(os.path.join(root, name))
