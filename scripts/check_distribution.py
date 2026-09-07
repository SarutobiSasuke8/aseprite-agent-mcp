"""Inspect archives without extracting them; keep machine/private context out."""
import tarfile, zipfile
from pathlib import Path
blocked = [b"C:\\Users\\", b"C:\\Dev\\", b"Cryptic Grove", b"sarut"]
count=0
for archive in Path('dist').glob('*'):
    if archive.suffix=='.whl':
        with zipfile.ZipFile(archive) as z: entries=[(n,z.read(n)) for n in z.namelist()]
    elif archive.name.endswith('.tar.gz'):
        with tarfile.open(archive) as t: entries=[(m.name,t.extractfile(m).read()) for m in t.getmembers() if m.isfile()]
    else: continue
    count+=1
    assert any(n.endswith('NOTICE') for n,_ in entries), 'NOTICE missing'
    assert any(n.endswith('LICENSE') for n,_ in entries), 'LICENSE missing'
    for name,data in entries:
        if name.endswith('check_distribution.py'): continue
        assert not any(p in data for p in blocked), f'Private context in {name}'
        assert not any(p in name for p in ['BUILD_PLAN.md','AGENTS.md','node_modules','workspace/']), name
assert count>=2, 'Build wheel and sdist first'
print('Distribution boundary and licence checks passed')
