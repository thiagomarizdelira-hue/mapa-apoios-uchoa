import csv,sys,json,collections,unicodedata,re
d=json.load(open(sys.argv[1]+'/dados.json')); src=sys.argv[2]; out=sys.argv[3]
def norm(s): return re.sub(r'[^A-Z ]','',unicodedata.normalize('NFKD',s.upper()).encode('ascii','ignore').decode()).strip()
def num(s): return float(s.replace('.','').replace(',','.') or 0)
mun={norm(m['nome']):m['id'] for m in d['municipios']}
alias={'SAO CAETANO':'SAO CAITANO','BELEM DE SAO FRANCISCO':'BELEM DO SAO FRANCISCO','IGUARACI':'IGUARACY','LAGOA DO ITAENGA':'LAGOA DE ITAENGA'}
# candidate names 2026 + elected
cands={}
for k,v in d['candFed'].items(): cands[norm(v['nome'])]=k
for v in d['deputados']: cands[norm(v['nome'])]=v['id']
SEN={'HUMBERTO COSTA','TERESA LEITAO','FERNANDO DUEIRE','JARBAS VASCONCELOS','FERNANDO BEZERRA COELHO','HUMBERTO COSTA'}
MUNNAT={'Município','Fundo Público da Administração Direta Municipal','Órgão Público do Poder Executivo Municipal','Autarquia Municipal','Fundação Pública de Direito Público Municipal'}
ACC={'COMISSAO':'Comissão','ECONOMICOS':'Econômicos','ECONOMICO':'Econômico','COMERCIO':'Comércio','DEFICIENCIA':'Deficiência','VIACAO':'Viação','AGRARIA':'Agrária','EDUCACAO':'Educação','TRANSPARENCIA':'Transparência','GOVERNANCA':'Governança','FISCALIZACA':'Fiscalização','MUDANCAS':'Mudanças','CLIMATICA':'Climática','AMAZONIA':'Amazônia','PUBLICO':'Público','SERV.PUBLICO':'Serv. Público',
'ANDRE':'André',
 'LEITAO':'Leitão',
 'SAUDE':'Saúde',
 'TULIO':'Túlio',
 'GADELHA':'Gadêlha',
 'MENDONCA':'Mendonça',
 'JOAO':'João',
 'JOSE':'José',
 'ANTONIO':'Antônio',
 'MARILIA':'Marília',
 'SEBASTIAO':'Sebastião',
 'INOCENCIO':'Inocêncio',
 'DESENV':'Desenvolvimento',
 'INTEGRACAO':'Integração',
 'EDUCACAO':'Educação',
 'SEGURANCA':'Segurança',
 'PUBLICA':'Pública',
 'CIENCIA':'Ciência',
 'COMUNICACAO':'Comunicação',
 'INOVACAO':'Inovação',
 'FISCALIZACAO':'Fiscalização',
 'MAGALHAES':'Magalhães',
 'ARAUJO':'Araújo',
 'GUIMARAES':'Guimarães',
 'TERCIO':'Tércio',
 'CAMARA':'Câmara',
 'AGRICULTURA':'Agricultura',
 'PECUARIA':'Pecuária',
 'ABASTECIMENTO':'Abastecimento',
 'TURISMO':'Turismo',
 'CULTURA':'Cultura',
 'URBANO':'Urbano',
 'DEFESA':'Defesa',
 'ASSUNCAO':'Assunção',
 'CONCEICAO':'Conceição',
 'LUCIO':'Lúcio',
 'CASSIO':'Cássio',
 'FABIO':'Fábio',
 'MARCIO':'Márcio',
 'SERGIO':'Sérgio',
 'ROGERIO':'Rogério',
 'VALERIA':'Valéria',
 'PAULAO':'Paulão',
 'SOSTENES':'Sóstenes',
 'ESPERIDIAO':'Esperidião',
 'DAMIAO':'Damião',
 'OTAVIO':'Otávio',
 'VITORIA':'Vitória',
 'JUNIOR':'Júnior',
 'ADMINISTRACAO':'Administração',
 'SERVICO':'Serviço',
 'REGIAO':'Região',
 'NACIONAL':'Nacional',
 'RELACOES':'Relações',
 'EXTERIORES':'Exteriores',
 'ESPORTE':'Esporte',
 'TRABALHO':'Trabalho',
 'EURICO':'Eurico',
 'OSSESIO':'Ossesio',
 'ARRAES':'Arraes'}
LOW={'E','DA','DE','DO','DOS','DAS'}
def pretty(a):
    a=a.replace('COM. ','COMISSÃO: ')
    out=[]
    for i,w in enumerate(a.split()):
        if i and w in LOW: out.append(w.lower()); continue
        if w=='COMISSÃO:': out.append('Comissão:'); continue
        k=w.rstrip(',');out.append(ACC[k]+w[len(k):] if k in ACC else w.capitalize())
    return ' '.join(out).replace('Comissão: da ','Comissão: ').replace('Comissão: de ','Comissão: ')

agg=collections.defaultdict(lambda:[0.0,0.0]); miss=collections.Counter(); autores={}
r=csv.DictReader(open(src+'/EmendasParlamentares_PorFavorecido.csv',encoding='latin1'),delimiter=';')
for row in r:
    if row['UF Favorecido']!='PE': continue
    n=norm(row['Município Favorecido']); n=alias.get(n,n)
    if n not in mun: miss[n]+=1; continue
    a=row['Nome do Autor da Emenda'].strip(); ano=row['Ano/Mês'][:4]; t=row['Tipo de Emenda']
    tk='I' if 'Individual' in t and 'Especiais' not in t else 'P' if 'Especiais' in t else 'B' if 'Bancada' in t else 'C' if 'Comiss' in t else 'R'
    agg[(mun[n],a,ano,tk)][0 if row['Natureza Jurídica'] in MUNNAT else 1]+=num(row['Valor Recebido'])
    if a not in autores:
        na=norm(a); 
        if a.startswith('BANCADA') : cls='bancada'
        elif a.startswith('COM.') or a.startswith('COMISS'): cls='comissao'
        elif a.startswith('RELATOR'): cls='relator'
        elif na in SEN: cls='senador'
        else: cls='parlamentar'
        sq=cands.get(na)
        autores[a]={'nome':pretty(a),'cls':cls,'sq':sq}
print('miss',miss.most_common(10),file=sys.stderr)
# manual fixes for known name variants
FORCE={'GUILHERME UCHOA':'170002540312','FERNANDO COELHO FILHO':[v['id'] for v in d['deputados'] if v['nome']=='Fernando Filho'][0],'MARCELO RAMOS':None}
for a,v in autores.items():
    if a in FORCE: v['sq']=FORCE[a]
alist=sorted(autores); aidx={a:i for i,a in enumerate(alist)}
em=collections.defaultdict(list)
for (m,a,ano,tk),(vp,vo) in agg.items():
    if vp+vo<1: continue
    em[m].append([aidx[a],int(ano),tk,round(vp),round(vo)])
json.dump({'fonte':'Portal da Transparência (CGU) — Emendas parlamentares por favorecido, valores pagos','atualizado':'24/11/2026',
  'autores':[autores[a] for a in alist],'mun':em},open(out,'w'),ensure_ascii=False,separators=(',',':'))
tot=sum(x[3] for v in em.values() for x in v)
print(len(alist),'autores',sum(len(v) for v in em.values()),'linhas',len(em),'municipios',round(tot/1e6),'M prefeituras',file=sys.stderr)
for a in alist:
    v=autores[a]
    if v['cls']=='parlamentar' and not v['sq']: print(' sem match:',a,file=sys.stderr)
