# Calendário de trade 2027: datas, papel de cada motor, participação real na venda e peso proposto do trade.
import json,pathlib,html,datetime as DT
R=pathlib.Path(__file__).resolve().parent.parent
F=R/'analise/calendario.json'
MESES=['Janeiro','Fevereiro','Março','Abril','Maio','Junho','Julho','Agosto','Setembro','Outubro','Novembro','Dezembro']
COR={'Cuidar':'#7C381F','Abastecer':'#596D49','Granel':'#AC834C','Celebrar':'#CA942A'}
MC=['Cuidar','Abastecer','Celebrar'];MR=['Cuidar','Abastecer','Granel','Celebrar']
NOME_V2={'Gourmet: Doces e chocolates':'Doces e chocolates','Gourmet: Azeites, molhos e antepastos':'Azeites e molhos','Gourmet: Massas e prontos':'Massas e prontos','Gourmet: Bebidas vegetais e básicos':'Básicos do Gourmet','Gourmet: Biscoitos e snacks':'Biscoitos','Gourmet: Cafés, vinhos e presenteáveis':'Cafés e presentes','Geladeira':'Geladeira','Sem Glúten':'Sem Glúten'}
NOME={'Vitaminas de A a Z':'Vitaminas','Colágeno e Beleza':'Colágeno','Equilíbrio e Bem-Estar':'Bem-estar','Saúde Intestinal':'Intestino','Café e cápsulas':'Cafés funcionais','Farinhas e despensa':'Farinhas','Despensa sem setor':'Despensa','Peso e Composição':'Peso e composição','Empório: Chocolates e doces finos':'Chocolates','Empório: Azeites e vinagres':'Azeites','Empório: Massas e risotos':'Massas','Empório: Geleias e mel':'Geleias e mel','Empório: Molhos e condimentos':'Molhos','Empório: Cafés especiais':'Cafés especiais'}
# v2: datas e níveis de ação da tabela oficial da rede (devolutiva de 16/11/2026, p. 12). Nível: Campanha, Apoio ao trade, Conteúdo ou Em aberto.
# Datas de conscientização são conteúdo, sem produto vinculado. Corpus Christi e as datas que a rede não trabalha saíram.
SUGESTOES='Dia Mundial do Café (14/04), Dia do Profissional de Educação Física (01/09) e Dia Mundial da Alimentação (16/10)'
CAL=[
 dict(m=1,dt=[('01/01','Verão e volta à rotina',1,'Campanha'),('01/01','Ano novo, rotina nova',0,'Conteúdo'),('20/01','Volta às aulas',0,'Conteúdo')],foco='Verão e volta à rotina',alvo=None,
  C='Rotina nova: creatina, colágeno e bem-estar, com conteúdo de começo de ano',A='Verão: hidratação, barras e granel em porção. Volta às aulas entra como conteúdo',E='Cozinhar em casa no verão: azeite, temperos e conservas',
  ponta='Rotina nova',mesa='Verão leve',enc='1 creatina, 1 granel, 1 Gourmet',proj='Início do piloto (18/01)',peso=(55,35,10)),
 dict(m=2,dt=[('06/02','Carnaval',1,'Campanha'),('14/02',"Valentine's Day",0,'Apoio ao trade')],foco='Carnaval',alvo=(2,6),
  C='Carnaval: hidratação, eletrólitos e recuperação',A='Barras e snacks para o feriado, granel em porção',E="Valentine's Day: chocolate e presente a dois, como apoio ao trade",
  ponta='Hidratação e energia',mesa='Presente a dois',enc='1 eletrólito, 1 barra, 1 chocolate',proj='',peso=(50,35,15)),
 dict(m=3,dt=[('08/03','Dia Internacional da Mulher',1,'Campanha'),('15/03','Dia do Consumidor',1,'Campanha'),('28/03','Páscoa',1,'Campanha')],foco='Mulher, Consumidor e Páscoa',alvo=(3,28),
  C='Dia da Mulher: colágeno, saúde da mulher e Vivea, sem alegação. Dia do Consumidor: ver a tela das campanhas',A='Páscoa: kit receita com farinha, cacau em pó e castanhas do granel, com a receita impressa',E='Páscoa: ovos e chocolate de origem, colomba e geleias',
  ponta='Dia do Consumidor, de 12 a 15/03',mesa='Páscoa',enc='1 colágeno, 1 kit receita, 1 chocolate',proj='Leitura da semana 6',peso=(35,20,45)),
 dict(m=4,dt=[],foco='Mês sem campanha da rede: execução e outono',alvo=None,
  C='Outono: ômegas e vitaminas como conteúdo, sem alegação',A='Chás e cafés para o frio que começa',E='Depois da Páscoa, o que sobra sai por regra, sem queima',
  ponta='Rotina de outono',mesa='Café e chá da tarde',enc='1 ômega, 1 chá, 1 café',proj='Leitura final do piloto (11/04)',peso=(50,35,15)),
 dict(m=5,dt=[('06/05','Aniversário de 16 anos da Divina Terra',1,'Campanha'),('09/05','Dia das Mães',1,'Campanha')],foco='16 anos da rede e Dia das Mães',alvo=(5,6),
  C='16 anos: Vivea e 16 líderes da rede em destaque. Mães: colágeno e bem-estar para presentear',A='Aniversário: granel com oferta de 16 anos',E='Mães: cestas por faixa de preço, geleias e chocolates',
  ponta='16 anos da Divina Terra',mesa='Presentes para as mães',enc='1 Vivea, 1 granel, 1 cesta',proj='Onda 2',peso=(35,20,45)),
 dict(m=6,dt=[('12/06','Dia dos Namorados',1,'Apoio ao trade'),('21/06','Início do inverno',0,'Apoio ao trade'),('24/06','Festa Junina',0,'Conteúdo')],foco='Inverno e Namorados',alvo=(6,12),
  C='Inverno: ômegas, vitaminas e imunidade, sem alegação',A='Chás e cafés do frio. Festa Junina entra como conteúdo, com o granel',E='Namorados: chocolate e presente a dois',
  ponta='Inverno',mesa='Presente a dois',enc='1 ômega, 1 chá, 1 chocolate',proj='',peso=(45,30,25)),
 dict(m=7,dt=[('01/07','Férias de julho e volta às aulas',1,'Apoio ao trade')],foco='Férias de julho',alvo=None,
  C='Kids nas férias e na volta às aulas',A='Lancheira: barras, snacks e granel em porção',E='Massas e sopas do frio',
  ponta='Lancheira',mesa='Noite fria em casa',enc='1 kids, 1 barra, 1 massa',proj='Onda 3',peso=(40,40,20)),
 dict(m=8,dt=[('08/08','Dia dos Pais',1,'Campanha'),('31/08','Dia do Nutricionista',1,'Campanha')],foco='Pais e Nutricionista',alvo=(8,8),
  C='Dia do Nutricionista: encontro na loja, amostras e cartão de indicação. Pais: proteína e creatina para presentear',A='Cafés funcionais e barras',E='Pais: café especial, conservas e presente',
  ponta='Presente para o pai',mesa='Café e tábua',enc='1 proteína, 1 café, 1 presente',proj='',peso=(55,15,30)),
 dict(m=9,dt=[('15/09','Dia do Cliente',1,'Campanha'),('01/09','Setembro Amarelo',0,'Conteúdo')],foco='Semana do Cliente',alvo=(9,15),
  C='Semana do Cliente: ver a tela das campanhas. Setembro Amarelo: conteúdo de cuidado com a mente, sem produto vinculado',A='Granel: oferta de cliente, o maior peso do granel no ano',E='1 oferta de Gourmet no encarte',
  ponta='Semana do Cliente',mesa='Lanche leve',enc='1 granel, 1 referência, 1 Gourmet',proj='',peso=(35,50,15)),
 dict(m=10,dt=[('12/10','Dia das Crianças',1,'Campanha'),('01/10','Outubro Rosa',0,'Conteúdo'),('15/10','Dia do Professor',0,'Em aberto')],foco='Dia das Crianças',alvo=(10,12),
  C='Kids: a linha infantil inteira em destaque, com faixa simples e sem promessa. Outubro Rosa: conteúdo, sem produto vinculado',A='Lancheira e granel para as crianças',E='Doces sem açúcar e presentes para crianças',
  ponta='Dia das Crianças',mesa='Lancheira',enc='1 kids, 1 lanche, 1 doce',proj='',peso=(35,40,25)),
 dict(m=11,dt=[('26/11','Black Friday',1,'Campanha'),('01/11','Novembro Azul',0,'Conteúdo')],foco='Black Friday',alvo=(11,26),
  C='Black Friday: ver a tela das campanhas. Novembro Azul: conteúdo, sem produto vinculado',A='Granel e barras em combo de Black Friday',E='Prévia de Natal: cestas montadas',
  ponta='Black Friday',mesa='Prévia de Natal',enc='3 combos, 1 granel, 1 cesta',proj='Pedido de Natal fechado',peso=(60,25,15)),
 dict(m=12,dt=[('25/12','Natal',1,'Campanha'),('31/12','Réveillon',1,'Campanha'),('01/12','Final de ano e férias',0,'Em aberto')],foco='Natal e Réveillon',alvo=(12,25),
  C='Suplemento recua no mês: garantir reposição, sem verba extra',A='Castanhas, frutas secas e despensa para a ceia',E='Natal: ponta, mesa e cestas. Réveillon: espumante com licença e castanhas',
  ponta='Natal',mesa='Ceia e presentes',enc='1 cesta, 1 castanha, 1 chocolate',proj='Planograma v2',peso=(10,25,65)),
]
NIV={'Campanha':'camp','Apoio ao trade':'apoio','Conteúdo':'cont','Em aberto':'aberto'}
def calcula():
    import pandas as pd
    a=pd.read_pickle(R/'analise/vendas5.pkl');a['setorf']=a.setorf.astype(str)
    M={**{c:'Cuidar' for c in ['Proteínas','Creatina','Vitaminas de A a Z','Ômegas','Colágeno e Beleza','Equilíbrio e Bem-Estar','Performance','Café e cápsulas','Longevidade','Saúde Intestinal','Imunidade','Kids','Peso e Composição','Suplementos sem setor']},**{c:'Abastecer' for c in ['Barras e snacks','Chás','Sem Glúten','Geladeira']},'Granel':'Granel'}
    a['mot']=a.setorf.map(M);a.loc[a.setorf.str.startswith('Gourmet'),'mot']='Celebrar';a=a[a.mot.notna()];a['mm']=a.p.str[5:].astype(int)
    t=a.pivot_table(index='mm',columns='mot',values='valor',aggfunc='sum');sh=t.div(t.sum(axis=1),axis=0)*100
    vl=a.groupby('p').agg(v=('valor','sum'),l=('loja','nunique'));vl['pl']=vl.v/vl.l;pl={}
    for p,x in vl.iterrows(): pl[int(p[5:])]=pl.get(int(p[5:]),0)+x.pl
    tot=a.groupby('setorf').valor.sum();ok=tot[tot>=100000].index
    c=a[a.setorf.isin(ok)].pivot_table(index='setorf',columns='mm',values='valor',aggfunc='sum').fillna(0);mt=a.groupby('mm').valor.sum();cs=c.div(mt,axis=1)*100;ix=cs.div(cs.mean(axis=1),axis=0)*100
    d={}
    for m in range(1,13):
        s=ix[m].sort_values(ascending=False);s=s[~s.index.isin(['Suplementos sem setor'])]
        d[m]=dict(sh={k:round(float(sh.loc[m,k]),1) for k in MR},pl=round(float(pl[m])),alta=[[NOME_V2.get(k,NOME.get(k,k)),int(round(v-100))] for k,v in s.items() if v>=105][:4])
    F.write_text(json.dumps(d,ensure_ascii=False));return d
def dados():
    return {int(k):v for k,v in json.loads(F.read_text()).items()} if F.exists() else calcula()
def br(x,c=0): return (f'{x:.{c}f}').replace('.',',')
def prazos(i):
    a=i['alvo']
    if not a: return None
    d=DT.date(2027,*a);f=lambda n:(d-DT.timedelta(days=n)).strftime('%d/%m')
    return f(45),f(15),(d+DT.timedelta(days=1)).strftime('%d/%m')
CSS='''
.nv{display:inline-block;width:9px;height:9px;border-radius:50%;margin-right:4px;vertical-align:1px}.nv-camp{background:var(--paprica)}.nv-apoio{background:var(--oliva)}.nv-cont{background:var(--linho)}.nv-aberto{background:#fff;box-shadow:inset 0 0 0 1.5px var(--cinza)}
.nvt{display:inline-block;margin-left:6px;font-style:normal;font-size:11.5px;font-weight:600;padding:1px 7px;border-radius:9px;color:#fff;vertical-align:1px}.nvt.nv-cont{color:var(--terra)}.nvt.nv-aberto{color:var(--cinza)}.s-cal1 .cg .d span.sem{color:var(--cinza);font-style:italic}
.s-cal1 .cg{display:grid;grid-template-columns:118px repeat(12,1fr);gap:3px;margin-top:10px;font-size:12.5px;line-height:1.16}.s-cal1 .cg>div{padding:5px 5px;border-radius:5px;background:#fff;min-width:0}.s-cal1 .cg .h{background:var(--terra);color:var(--iogurte);font:400 16px var(--serif);text-align:center}.s-cal1 .cg .l{background:none;font-weight:600;color:var(--terra);display:flex;flex-direction:column;justify-content:center;padding-left:0}.s-cal1 .cg .l small{font-weight:400;color:var(--cinza);font-size:11px}
.s-cal1 .cg .d b{display:block;color:var(--choco);font-weight:600}.s-cal1 .cg .d span{display:block;margin-top:2px}.s-cal1 .pv{display:flex;flex-direction:column;justify-content:flex-end;height:60px;text-align:center;font-weight:600;color:var(--terra)}.s-cal1 .pv i{display:block;background:var(--linho);border-radius:3px 3px 0 0;margin-top:2px}.s-cal1 .pv.top i{background:var(--choco)}
.s-cal1 .r{text-align:center;font-weight:600;font-size:14px}.s-cal1 .r.u{outline:2px solid var(--paprica);outline-offset:-2px}
.s-cal1 .st{display:flex;flex-direction:column;height:92px;border-radius:4px;overflow:hidden}.s-cal1 .st span{display:flex;align-items:center;justify-content:center;color:#fff;font-weight:600;font-size:12px;min-height:0}.s-cal1 .st span.k{color:var(--terra)}
.s-cal1 .a{font-size:11.5px;color:var(--terra)}.s-cal1 .a em{display:block;font-style:normal;margin-bottom:2px}.s-cal1 .a em b{color:var(--oliva);font-weight:600}.s-cal1 .pj{font-size:11.5px;color:var(--choco);font-weight:600;background:var(--aveia)!important}
.s-cal2 .aba.on{color:var(--choco);font-weight:600;box-shadow:inset 0 -2px 0 var(--choco)}
.s-cal2 .cm{display:grid;grid-template-columns:300px 1fr 330px;gap:12px;margin-top:10px;align-items:stretch}.s-cal2 .bx{background:#fff;border-radius:10px;padding:12px 14px}.s-cal2 h4{font:400 24px/1.1 var(--serif);color:var(--choco);margin:0 0 3px}.s-cal2 .sb{font-size:14px;color:var(--cinza);margin-bottom:8px}.s-cal2 .dt{list-style:none;padding:0;margin:0}.s-cal2 .dt li{display:grid;grid-template-columns:78px 1fr;gap:8px;padding:6px 0;border-top:1px solid var(--aveia);font-size:14px;line-height:1.2}.s-cal2 .dt li b{color:var(--terra);font-weight:600}.s-cal2 .dt li.pr span{font-weight:600;color:var(--choco)}
.s-cal2 .pz{margin-top:10px;display:grid;gap:4px;font-size:13px;color:var(--terra)}.s-cal2 .pz b{font-weight:600}.s-cal2 .pz div{display:flex;justify-content:space-between;background:var(--iogurte);border-radius:6px;padding:4px 8px}
.s-cal2 .mt{display:grid;gap:8px}.s-cal2 .mo{border-left:6px solid var(--c);background:#fff;border-radius:8px;padding:9px 12px}.s-cal2 .mo b{display:block;color:var(--c);font-weight:600;font-size:13px}.s-cal2 .mo p{margin:2px 0 0;font-size:15px;line-height:1.22;color:var(--terra)}
.s-cal2 .es{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-top:8px}.s-cal2 .es div{background:var(--aveia);border-radius:8px;padding:8px 10px;font-size:13.5px;line-height:1.2;color:var(--terra)}.s-cal2 .es b{display:block;font-weight:600;font-size:12px;color:var(--choco);margin-bottom:2px}
.s-cal2 .ba{margin-bottom:8px;font-size:13px;color:var(--terra)}.s-cal2 .ba>span{display:flex;justify-content:space-between;font-weight:600}.s-cal2 .ba i{display:block;height:9px;border-radius:3px;margin-top:2px;background:var(--c)}.s-cal2 .ba i.pp{opacity:.45;margin-top:2px}.s-cal2 .ba small{font-weight:400;color:var(--cinza)}
.s-cal2 .alt{display:flex;flex-wrap:wrap;gap:5px;margin-top:4px}.s-cal2 .alt span{background:var(--matcha);border-radius:12px;padding:3px 9px;font-size:12.5px;color:var(--terra)}.s-cal2 .lt{font-size:12px;font-weight:600;color:var(--choco);margin:9px 0 3px}
'''
def ano():
    d=dados();mx=max(v['pl'] for v in d.values());mn=min(v['pl'] for v in d.values());g='<div class="l"></div>'+''.join(f'<div class="h">{m[:3]}</div>' for m in MESES)
    def _datas(i):
        if not i['dt']: return '<div class="d"><span class="sem">Sem data da rede</span></div>'
        pr=''.join(f'<span><b><i class="nv nv-{NIV[nv]}" title="{nv}"></i>'+html.escape(n)+'</b>'+(html.escape(a) if '/' in a else '')+'</span>' for a,n,p,nv in i['dt'] if p)
        ou=''.join(f'<span><i class="nv nv-{NIV[nv]}" title="{nv}"></i>'+html.escape(n)+(' '+a if '/' in a else '')+'</span>' for a,n,p,nv in i['dt'] if not p)
        return '<div class="d">'+pr+ou+'</div>'
    g+='<div class="l">Datas de 2027</div>'+''.join(_datas(i) for i in CAL)
    g+='<div class="l">Venda por loja<small>R$ mil no mês</small></div>'+''.join(f'<div class="pv{" top" if d[i["m"]]["pl"]==mx else ""}">{round(d[i["m"]]["pl"]/1000)}<i style="height:{8+30*(d[i["m"]]["pl"]-mn)/(mx-mn):.0f}px"></i></div>' for i in CAL)
    for k in MR:
        g+=f'<div class="l" style="color:{COR[k]}">{"Abastecer" if k=="Abastecer" else k}<small>{"% real da venda" if k=="Cuidar" else "sem granel" if k=="Abastecer" else "parte de Abastecer" if k=="Granel" else "% real da venda"}</small></div>'
        vs=[d[i['m']]['sh'][k] for i in CAL];hi=max(vs)
        g+=''.join(f'<div class="r{" u" if d[i["m"]]["sh"][k]==hi else ""}" style="color:{COR[k]}">{br(d[i["m"]]["sh"][k],1)}</div>' for i in CAL)
    g+='<div class="l">Peso do trade<small>% das ativações, proposta</small></div>'
    for i in CAL:
        p=i['peso'];g+='<div style="padding:0"><div class="st">'+''.join(f'<span class="{"k" if k=="Celebrar" else ""}" style="flex:{v} 0 0;background:{COR[k]}">{v}</span>' for k,v in zip(['Celebrar','Abastecer','Cuidar'],[p[2],p[1],p[0]]))+'</div></div>'
    g+='<div class="l">Pesa mais<small>sobre a média da categoria</small></div>'+''.join('<div class="a">'+''.join(f'<em>{html.escape(n)} <b>+{v}%</b></em>' for n,v in d[i['m']]['alta'][:2])+'</div>' for i in CAL)
    g+='<div class="l">Projeto</div>'+''.join(f'<div class="pj">{html.escape(i["proj"])}</div>' if i['proj'] else '<div style="background:none"></div>' for i in CAL)
    return f'<div class="cg">{g}</div>'
def _barra(k,re_,pr):
    return f'<div class="ba" style="--c:{COR[k]}"><span>{k}<small>hoje {br(re_,1)}% · trade {pr}%</small></span><i style="width:{max(re_,1):.0f}%"></i><i class="pp" style="width:{max(pr,1)}%"></i></div>'
def meses():
    d=dados();bts='';pns=''
    for j,i in enumerate(CAL):
        m=i['m'];x=d[m];nm=MESES[m-1];pz=prazos(i)
        dts=''.join(f'<li class="{"pr" if p else ""}"><b>{html.escape(a)}</b><span>{html.escape(n)}<em class="nvt nv-{NIV[nv]}">{nv}</em></span></li>' for a,n,p,nv in i['dt']) or '<li><b>Abril</b><span>Sem campanha da rede no mês<em class="nvt nv-aberto">Execução</em></span></li>'
        prz=(f'<div class="pz"><div><span>Plano e pedido fechados</span><b>{pz[0]}</b></div><div><span>Material na loja</span><b>{pz[1]}</b></div><div><span>Desmontar</span><b>{pz[2]}</b></div></div>' if pz else '<div class="pz"><div><span>Tema do mês inteiro: material na loja</span><b>até o dia 1º</b></div></div>')
        real=x['sh'];abast=real['Abastecer']+real['Granel']
        barras=_barra('Cuidar',real['Cuidar'],i['peso'][0])+_barra('Abastecer',abast,i['peso'][1])+_barra('Celebrar',real['Celebrar'],i['peso'][2])
        alta=''.join(f'<span>{html.escape(n)} +{v}%</span>' for n,v in x['alta'])or'<span>Nenhuma categoria 5% acima da média</span>'
        proj=('<div class="lt">Projeto</div><div style="font-size:14px;color:var(--terra)">'+html.escape(i['proj'])+'</div>') if i['proj'] else ''
        bts+=f'<button class="aba pa{" on" if j==0 else ""}" data-k="cal{m}">{nm[:3]}</button>'
        pns+=f'<div class="painel{" on" if j==0 else ""}" data-k="cal{m}"><div class="cm"><div class="bx"><h4>{nm}</h4><div class="sb">{html.escape(i["foco"])}. Venda por loja: R$ {round(x["pl"]/1000)} mil</div><ul class="dt">{dts}</ul>{prz}</div><div><div class="mt"><div class="mo" style="--c:{COR["Cuidar"]}"><b>Cuidar</b><p>{html.escape(i["C"])}</p></div><div class="mo" style="--c:{COR["Abastecer"]}"><b>Abastecer</b><p>{html.escape(i["A"])}</p></div><div class="mo" style="--c:#9a6d12"><b>Celebrar</b><p>{html.escape(i["E"])}</p></div></div><div class="es"><div><b>Ponta</b>{html.escape(i["ponta"])}</div><div><b>Mesa ou ponta extra</b>{html.escape(i["mesa"])}</div><div><b>Encarte</b>{html.escape(i["enc"])}</div></div></div><div class="bx"><div class="lt" style="margin-top:0">Hoje na venda e peso no trade</div>{barras}<div class="lt">Categorias que pesam mais neste mês</div><div class="alt">{alta}</div>{proj}</div></div></div>'
    return f'<div data-abas class="pa-abas"><div class="abas">{bts}</div>{pns}</div>'
def manual():
    d=dados();lin=''
    for i in CAL:
        x=d[i['m']];r_=x['sh'];pz=prazos(i)
        lin+=f'<tr><td><b>{MESES[i["m"]-1]}</b></td><td>{"; ".join(html.escape((n+" "+a if "/" in a else n)+" ("+nv+")") for a,n,p,nv in i["dt"]) or "Sem campanha da rede"}</td><td>{html.escape(i["C"])}</td><td>{html.escape(i["A"])}</td><td>{html.escape(i["E"])}</td><td class="np">{br(r_["Cuidar"],1)} · {br(r_["Abastecer"]+r_["Granel"],1)} · {br(r_["Celebrar"],1)}</td><td class="np">{i["peso"][0]} · {i["peso"][1]} · {i["peso"][2]}</td><td class="np">{(pz[0]+" e "+pz[1]) if pz else "até o dia 1º"}</td></tr>'
    return f'<table class="tb"><thead><tr><th>Mês</th><th>Datas de 2027 e nível da rede</th><th>Cuidar</th><th>Abastecer</th><th>Celebrar</th><th>% real da venda: Cuidar · Abastecer · Celebrar</th><th>% do trade, proposta</th><th>Plano fechado e material na loja</th></tr></thead><tbody>{lin}</tbody></table>'
def kit():
    d=dados();L=[]
    for i in CAL:
        x=d[i['m']];r_=x['sh'];pz=prazos(i) or ('','','')
        L.append([MESES[i['m']-1],'; '.join((n+' '+a if '/' in a else n)+' ('+nv+')' for a,n,p,nv in i['dt']) or 'Sem campanha da rede',i['foco'],i['C'],i['A'],i['E'],i['ponta'],i['mesa'],i['enc'],r_['Cuidar'],r_['Abastecer'],r_['Granel'],r_['Celebrar'],i['peso'][0],i['peso'][1],i['peso'][2],x['pl'],', '.join(f'{n} +{v}%' for n,v in x['alta']),pz[0],pz[1],pz[2],i['proj']])
    return L
