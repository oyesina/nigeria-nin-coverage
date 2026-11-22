import pandas as pd, numpy as np, sys
od=sys.argv[1]
enr=pd.read_csv(f'{od}/nin_enrolment_by_state.csv',parse_dates=['as_of'])
wp={'Abia':3924169.25,'Adamawa':6006481.456,'Akwa Ibom':4281013.948,'Anambra':5788664.686,'Bauchi':8781376.998,'Benue':9067209.083,'Borno':6269578.236,'Bayelsa':2523453.676,'Cross River':2566393.397,'Delta':7712872.39,'Ebonyi':2567908.144,'Edo':6633884.179,'Ekiti':3060453.429,'Enugu':5104971.815,'FCT':3735905.649,'Gombe':4477433.215,'Imo':6592131.419,'Jigawa':7645450.17,'Kebbi':4015574.776,'Kaduna':11233188.31,'Kano':18771133.63,'Kogi':4479439.153,'Katsina':10522942.91,'Kwara':4687187.345,'Lagos':12582855.93,'Nasarawa':3598556.717,'Niger':7303220.252,'Ogun':12934343.05,'Ondo':5658396.028,'Osun':5595659.114,'Oyo':8988216.774,'Plateau':5771080.854,'Rivers':6863907.13,'Sokoto':4373777.932,'Taraba':4473844.385,'Yobe':5370897.311,'Zamfara':3564209.261}
npc={'Abia':4143100,'Adamawa':4902100,'Akwa Ibom':4979400,'Anambra':5953500,'Bauchi':8308800,'Bayelsa':2537400,'Benue':6141300,'Borno':6111500,'Cross River':4406200,'Delta':5636100,'Ebonyi':3242500,'Edo':4777000,'Ekiti':3592200,'Enugu':4690100,'FCT':3067500,'Gombe':3960100,'Imo':5459300,'Jigawa':7499100,'Kaduna':9032200,'Kano':15462200,'Katsina':10368500,'Kebbi':5563900,'Kogi':4466800,'Kwara':3551000,'Lagos':13491800,'Nasarawa':2886000,'Niger':6783300,'Ogun':6379500,'Ondo':5316600,'Osun':4435800,'Oyo':7976100,'Plateau':4717300,'Rivers':7476800,'Sokoto':6391000,'Taraba':3609800,'Yobe':3649600,'Zamfara':5833500}
assert len(wp)==37==len(npc) and set(wp)==set(npc)
region={'North Central':['Benue','FCT','Kogi','Kwara','Nasarawa','Niger','Plateau'],'North East':['Adamawa','Bauchi','Borno','Gombe','Taraba','Yobe'],'North West':['Jigawa','Kaduna','Kano','Katsina','Kebbi','Sokoto','Zamfara'],'South East':['Abia','Anambra','Ebonyi','Enugu','Imo'],'South South':['Akwa Ibom','Bayelsa','Cross River','Delta','Edo','Rivers'],'South West':['Ekiti','Lagos','Ogun','Ondo','Osun','Oyo']}
reg={s:r for r,ss in region.items() for s in ss}
assert set(reg)==set(wp)
# national UN WPP 2024 mid-year totals; interpolate to each as_of date
un=pd.Series({2021:218.53e6,2022:223.15e6,2023:227.88e6,2024:232.68e6,2025:237.53e6,2026:242.43e6})
def un_pop(d):
    t=d.year+(d.dayofyear-182)/365.25
    return float(np.interp(t,un.index.values,un.values))
NPC_GROWTH=(221250127/216783381)  # NPC 2023 vs 2022 national, ~2.06%/yr
def npc_pop(s,d):
    yrs=(d-pd.Timestamp('2022-03-21')).days/365.25
    return npc[s]*NPC_GROWTH**yrs
ADULT16=1-0.4052-(0.0576+0.0555)/5  # UN/WB 2025: 0-14 = 40.52%; age 15 ~ one fifth of 15-19 (11.31%)
wp_share={s:v/sum(wp.values()) for s,v in wp.items()}
rows=[]
for _,r in enr.iterrows():
    s=r.state; d=r.as_of
    base=dict(r)
    base['region']=reg.get(s,'Diaspora')
    if s=='Diaspora':
        for sc in ['WorldPop 2025 (UN-scaled)','NPC/NBS projection']:
            rows.append({**base,'pop_scenario':sc,'population_total':np.nan})
        continue
    rows.append({**base,'pop_scenario':'WorldPop 2025 (UN-scaled)','population_total':wp_share[s]*un_pop(d)})
    rows.append({**base,'pop_scenario':'NPC/NBS projection','population_total':npc_pop(s,d)})
m=pd.DataFrame(rows)
m['population_16plus']=m.population_total*ADULT16
for k,col in [('total','population_total'),('16plus','population_16plus')]:
    m[f'uncaptured_{k}']=(m[col]-m.total)
    m[f'coverage_{k}']=m.total/m[col]
    m[f'gap_to_95_{k}']=(0.95*m[col]-m.total).clip(lower=0)
m['female_share']=m.female/m.total
m['latest']=m.as_of==m.as_of.max()
m['as_of']=m.as_of.dt.date
m=m.drop(columns=['note']).merge(enr[['report','note']].drop_duplicates(),on='report',how='left')
m.to_csv(f'{od}/nin_coverage_model.csv',index=False)
L=m[m.latest & (m.state!='Diaspora')]
for sc,g in L.groupby('pop_scenario'):
    P=g.population_total.sum(); P16=g.population_16plus.sum(); E=g.total.sum()
    print(f'{sc}: pop {P/1e6:.1f}M, 16+ {P16/1e6:.1f}M, enrolled(in-country) {E/1e6:.2f}M, cov {E/P:.1%}, cov16 {E/P16:.1%}, uncaptured {(P-E)/1e6:.1f}M / 16+ {(P16-E)/1e6:.1f}M; >100% states(16+): {list(g[g.coverage_16plus>1].state)}')
print('ADULT16',round(ADULT16,4),'rows',len(m))
