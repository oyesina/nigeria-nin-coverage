import re, sys, csv, datetime as dt
from dateutil import parser as dp
src=sys.argv[1]; out=sys.argv[2]
blocks=open(src).read().split('##')[1:]
NAME={'nassarawa':'Nasarawa','diaspora':'Diaspora','fct abuja':'FCT','akwa-ibom':'Akwa Ibom','cross-river':'Cross River'}
rows=[]; issues=[]
for b in blocks:
    lines=b.strip().split('\n'); slug,head=lines[0].split('|',1)
    m=re.search(r'as at (.*)$',head); ds=m.group(1) if m else ''
    note=''
    try:
        d=dp.parse(ds, default=dt.datetime(2022,1,1)).date() if re.search(r'\d{1,2}',ds) and not re.fullmatch(r'\d{4}',ds.strip()) else None
    except Exception: d=None
    if slug=='march-2023': d=dt.date(2023,3,31); note='as-of date not stated on page; assumed end of March 2023'
    seen=set(); total=None
    for ln in lines[2:]:
        st,f,mm,t=ln.split('|'); f,mm,t=int(f),int(mm),int(t)
        if slug=='sep-2021': pass  # header mislabeled; columns are F|M|T
        if slug=='october-2025' and st=='Abia' and mm==16849120: mm=1684912; issues.append('oct-2025 Abia male typo 16849120 -> 1684912 (F+M=T)')
        if re.search(r'total',st,re.I): total=(f,mm,t); continue
        key=st.lower(); s=NAME.get(key,st)
        if s in seen: issues.append(f'{slug}: duplicate row {s} dropped'); continue
        seen.add(s)
        if f+mm!=t: issues.append(f'{slug}: {s} F+M={f+mm} != T={t}')
        rows.append(dict(report=slug,as_of=d.isoformat(),state=s,female=f,male=mm,total=t,note=note))
    rs=[r for r in rows if r['report']==slug]
    st_sum=sum(r['total'] for r in rs)
    if total and st_sum!=total[2]: issues.append(f'{slug}: rows sum {st_sum} != stated total {total[2]} (diff {total[2]-st_sum})')
    if not total: issues.append(f'{slug}: no total row; computed {st_sum}')
    if len(rs)!=38: issues.append(f'{slug}: {len(rs)} rows (expected 37 states+FCT... incl diaspora=38)')
with open(out,'w',newline='') as fh:
    w=csv.DictWriter(fh,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
print(len(rows),'rows'); print('\n'.join(issues))
print(sorted({(r['report'],r['as_of']) for r in rows},key=lambda x:x[1]))
