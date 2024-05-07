from pathlib import Path

p = ''

path = Path(p).resolve()
path = Path(path)
print(path.is_dir())