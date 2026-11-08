import re,json,urllib.request,concurrent.futures,pathlib
p=pathlib.Path('reference/Awesome-Extruders'); out=p/'linked_readmes';out.mkdir(exist_ok=True)
links=dict(re.findall(r'\[([^\]]+)\]\((https://github.com/[^)]+)\)',(p/'README.md').read_text()))
def fetch(item):
 name,url=item; bits=url.split('?')[0].split('/')[3:]; owner,repo=bits[:2]; branch=bits[3] if len(bits)>3 and bits[2]=='tree' else None; sub='/'.join(bits[4:]) if branch else ''
 for b in ([branch] if branch else ['main','master']):
  for f in ['README.md','readme.md','README.MD']:
   u=f'https://raw.githubusercontent.com/{owner}/{repo}/{b}/'+(sub+'/' if sub else '')+f
   try:
    data=urllib.request.urlopen(u,timeout=12).read().decode(); target=out/(re.sub(r'[^a-zA-Z0-9_-]','_',name)+'.md'); target.write_text(data,encoding='utf8'); return name+' OK '+str(len(data))
   except: pass
 return name+' UNAVAILABLE'
with concurrent.futures.ThreadPoolExecutor(max_workers=12) as pool:
 for r in pool.map(fetch,links.items()): print(r)
