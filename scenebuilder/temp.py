from pathlib import Path

p = 'hd.json'

path = Path(p).resolve()
path = Path(path)
print(path.exists())
d = {'hi': 'hello', 'bye': 'goodbye'}
a = [1,2,3]
def temp(*args,**kwargs):
    print(*args)
    print(**kwargs)

temp(args = a, kwargs=d)