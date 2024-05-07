from pathlib import Path

p = ''

path = Path(p).resolve()
print(path.is_dir())