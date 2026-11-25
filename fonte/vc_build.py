import csv,json,sys,unicodedata,re,collections
D=sys.argv[1]; d=json.load(open(D+'/dados.json'))
def norm(s): return re.sub(r'[^A-Z ]','',unicodedata.normalize('NFKD',s.upper()).encode('ascii','ignore').decode()).strip()
order=[m['id'] for m in d['municipios']]; byname={norm(m['nome']):i for i,m in enumerate(d['municipios'])}
alias={'SAO CAETANO':'SAO CAITANO','BELEM DE SAO FRANCISCO':'BELEM DO SAO FRANCISCO','IGUARACI':'IGUARACY','LAGOA DO ITAENGA':'LAGOA DE ITAENGA'}
v=collections.defaultdict(lambda:collections.Counter()); miss=collections.Counter()
for r in csv.DictReader(open(D+'/votacao_2026_PE.csv',encoding='latin1'),delimiter=';'):
    if r['DS_CARGO'].upper()!='DEPUTADO FEDERAL': continue
    n=norm(r['NM_MUNICIPIO']); n=alias.get(n,n)
    if n not in byname: miss[n]+=1; continue
    q=int(r['QT_VOTOS_NOMINAIS_VALIDOS'] or 0)
    if q>0: v[r['SQ_CANDIDATO']][byname[n]]+=q
print('miss',miss)
out={sq:[x for i,q in sorted(c.items()) for x in (i,q)] for sq,c in v.items()}
bad=[(sq,sum(c.values()),d['candFed'][sq]['votosPE']) for sq,c in v.items() if sq in d['candFed'] and sum(c.values())!=d['candFed'][sq]['votosPE']]
print(len(out),'cands; mismatches',len(bad),bad[:3]); print('missing in candFed',[sq for sq in v if sq not in d['candFed']][:5])
json.dump(out,open(D+'/votos_cand.json','w'),separators=(',',':'))
