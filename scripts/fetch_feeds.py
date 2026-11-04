import json, time, urllib.request, os
UA={'User-Agent':'Mozilla/5.0 (feeds bot)'}
def get(url):
    with urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=20) as r:
        return json.loads(r.read().decode('utf-8'))
def find_items(o,d=0):
    if d>4 or o is None: return None
    if isinstance(o,list) and o and isinstance(o[0],dict) and 'title' in o[0]: return o
    if isinstance(o,dict):
        for v in o.values():
            r=find_items(v,d+1)
            if r: return r
    return None
os.makedirs('data',exist_ok=True)
now=int(time.time()*1000)
# macro calendar
try:
    ev=[]
    for u in ['https://nfs.faireconomy.media/ff_calendar_thisweek.json','https://nfs.faireconomy.media/ff_calendar_nextweek.json']:
        try: ev+= [x for x in get(u) if x.get('impact')=='High']
        except Exception as e: print('macro part fail',u,e)
    if ev:
        json.dump({'at':now,'items':ev},open('data/macro.json','w'),ensure_ascii=False)
except Exception as e: print('macro fail',e)
# news
for name,url in [('律动 BlockBeats','https://api.theblockbeats.news/v1/open-api/open-flash?size=30&page=1&type=push&lang=cn'),('CryptoCompare','https://min-api.cryptocompare.com/data/v2/news/?lang=EN')]:
    try:
        arr=find_items(get(url))
        if not arr: continue
        out=[]
        for x in arr[:30]:
            raw=x.get('create_time') or x.get('published_on') or x.get('add_time') or x.get('time')
            t=int(float(raw))*(1000 if raw and float(raw)<1e12 else 1) if raw else None
            out.append({'title':x.get('title',''),'content':(x.get('content') or x.get('body') or '')[:300],'url':x.get('link') or x.get('url') or '','t':t})
        json.dump({'at':now,'src':name,'items':out},open('data/news.json','w'),ensure_ascii=False)
        break
    except Exception as e: print('news fail',name,e)
