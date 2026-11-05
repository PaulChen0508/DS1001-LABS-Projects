"""Execute LABS-10 using the active Codespace Python environment."""
import json
import os
import sys
import tempfile
import zipfile
from pathlib import Path

import nbformat
from nbclient import NotebookClient

root = Path(__file__).resolve().parent
notebook_path = root / 'LABS-10_Analytics.ipynb'
with tempfile.TemporaryDirectory(prefix='lab10-kernel-') as scratch:
    kernel_root = Path(scratch)
    kernel_dir = kernel_root / 'kernels/lab10-active-env'
    kernel_dir.mkdir(parents=True)
    (kernel_dir / 'kernel.json').write_text(json.dumps({
        'argv': [sys.executable, '-m', 'ipykernel_launcher', '-f', '{connection_file}'],
        'display_name': 'PaulChen0508_env', 'language': 'python',
    }))
    previous_path = os.environ.get('JUPYTER_PATH', '')
    os.environ['JUPYTER_PATH'] = str(kernel_root) + (os.pathsep + previous_path if previous_path else '')
    nb = nbformat.read(notebook_path, as_version=4)
    NotebookClient(nb, timeout=240, kernel_name='lab10-active-env',
                   resources={'metadata': {'path': str(root)}}).execute()
    nbformat.write(nb, notebook_path)
    if previous_path:
        os.environ['JUPYTER_PATH'] = previous_path
    else:
        os.environ.pop('JUPYTER_PATH', None)

summary = json.loads((root / 'results/lab10/analysis_summary.json').read_text())
print('GitHub:', os.environ.get('GITHUB_USER', 'PaulChen0508'))
print('Codespace:', os.environ.get('CODESPACE_NAME', 'special engine'))
print(json.dumps(summary, indent=2))

bundle = root / 'lab10_completed_cloud.zip'
with zipfile.ZipFile(bundle, 'w', zipfile.ZIP_DEFLATED) as z:
    z.write(notebook_path, notebook_path.name)
    for folder in ['results/lab10', 'figures/lab10']:
        for file in (root / folder).rglob('*'):
            if file.is_file():
                z.write(file, file.relative_to(root))
print('Saved cloud notebook, results, figures, and', bundle.name)
