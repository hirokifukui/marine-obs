import re,json,sys,html
s=open(sys.argv[1],encoding='utf-8',errors='ignore').read()
out=[]
for blk in s.split('<div class="splst">')[1:]:
    t=lambda pat:(lambda m: html.unescape(re.sub('<[^>]+>',' ',m.group(1))).strip() if m else '')(re.search(pat,blk,re.S))
    name=t(r'gmap_title">.*?<span>(.*?)</span>')
    c=re.search(r'gmap_coord">\s*([\d.]+),\s*([\d.]+)',blk)
    out.append({"name":name,"lat":float(c.group(1)) if c else None,"lng":float(c.group(2)) if c else None,
      "access":t(r'AccessLabel[^>]*>(.*?)</span>').replace('■アクセス ：','').strip(),
      "level":t(r'LevelLabel[^>]*>(.*?)</span>').replace('■レベル ：','').strip(),
      "depth":t(r'DepthLabel[^>]*>(.*?)</span>').replace('■深 度 ：','').strip(),
      "current":t(r'NagareLabel[^>]*>(.*?)</span>').replace('■流 れ ：','').strip(),
      "desc":t(r'SpotDetailLabel[^>]*>(.*?)</span>\s*<span id').replace('■解説 ：','').strip(),
      "fish":t(r'FishDetailLabel[^>]*>(.*?)</span>\s*</div>').replace('■このエリアで見られる魚 ：','').strip()})
json.dump(out,open(sys.argv[2],'w',encoding='utf-8'),ensure_ascii=False,indent=1)
print(len(out)); print([ (o['name'],o['lat'],o['lng']) for o in out])
