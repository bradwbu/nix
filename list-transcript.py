import json
path='/home/brad/.openclaw/agents/main/sessions/e2d1a953-e2a5-4cf5-9deb-4349df47220a.jsonl'
with open(path) as f:\n    for line in f:\n        try:
            o=json.loads(line)
        except:
            continue
        if o.get('type')!='message':
            continue
        m=o.get('message',{})
        role=m.get('role','?')
        content=m.get('content','')
        ts=o.get('timestamp','')
        if isinstance(content,str):
            txt=content[:400]
        elif isinstance(content,list):
            parts=[]
            for c in content:
                if isinstance(c,dict):
                    if c.get('type')=='text':
                        parts.append(c.get('text','')[:400])
                    else:
                        parts.append('['+c.get('type','?')+':'+c.get('name',c.get('id',''))+']')
                else:
                    parts.append(str(c)[:100])
            txt=' | '.join(parts)[:600]
        else:
            txt=str(content)[:300]
        oid=o.get('id','')
        print(f"{ts} [{role}] {txt}")
        print('---')
