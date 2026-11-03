# Gera o kit de execução em planilha. Rodar da raiz: python3 fonte/kit.py
import pandas as pd,numpy as np,sys,re,warnings,pathlib
warnings.filterwarnings('ignore')
sys.path.insert(0,'analise');sys.path.insert(0,'fonte')
from openpyxl import Workbook
from openpyxl.styles import Font,PatternFill,Alignment,Border,Side
from openpyxl.utils import get_column_letter as CL
from openpyxl.worksheet.datavalidation import DataValidation
df=pd.read_pickle('analise/vendas4.pkl');L=pd.read_pickle('analise/lojas3.pkl');LC=pd.read_pickle('analise/lojas_cluster.pkl');prod=pd.read_pickle('analise/prod.pkl');BM=pd.read_pickle('analise/marcas.pkl')
TER,CHO,AVE,IOG,OLI,MAT,ACA='461D17','7C381F','E5DDD1','F7F5F1','596D49','A9C094','CA942A'
wb=Workbook()
def aba(nome,titulo,sub,cab,linhas,larg,fmt=None,cor=TER):
    ws=wb.create_sheet(nome);ws.sheet_view.showGridLines=False
    ws['A1']=titulo;ws['A1'].font=Font(name='Calibri',size=16,bold=True,color=CHO)
    ws['A2']=sub;ws['A2'].font=Font(size=10,italic=True,color='6F5F55')
    for j,c in enumerate(cab,1):
        x=ws.cell(row=4,column=j,value=c);x.font=Font(bold=True,color='FFFFFF');x.fill=PatternFill('solid',fgColor=cor);x.alignment=Alignment(wrap_text=True,vertical='center')
    for i,r in enumerate(linhas,5):
        for j,v in enumerate(r,1):
            x=ws.cell(row=i,column=j,value=v);x.alignment=Alignment(wrap_text=len(linhas)<500,vertical='top')
            if fmt and j in fmt:x.number_format=fmt[j]
    for j,w in enumerate(larg,1): ws.column_dimensions[CL(j)].width=w
    ws.freeze_panes='A5'
    if linhas: ws.auto_filter.ref=f'A4:{CL(len(cab))}{4+len(linhas)}'
    return ws
R='#,##0';P='0.0"%"'
# capa
ws=wb.active;ws.title='Leia-me';ws.sheet_view.showGridLines=False;ws.column_dimensions['A'].width=32;ws.column_dimensions['B'].width=100
ws['A1']='Divina Terra × 75 LAB · Kit de execução do piloto, v1';ws['A1'].font=Font(size=18,bold=True,color=CHO)
ws['A2']='Novembro de 2026. Acompanha a apresentação de estratégia avançada de trade marketing. Documento interno da rede: contém venda por loja e por SKU.';ws['A2'].font=Font(italic=True,color='6F5F55')
IDX=[('Árvore e naming','17 setores, motor, papel, prateleiras, nomes, glossário e participação real'),('De-para de SKUs','22.155 SKUs com venda: setor sugerido, curva, preço médio e ação sugerida. Primeira passada, a validar com compras'),('Empório lista','O que já vende, o que está parado no cadastro e o que cotar, por bloco'),('Preço de referência','50 SKUs candidatos, com colunas para a pesquisa de preço'),('Marcas peneira','1.432 marcas com faixa e ação sugerida'),('Lojas e quadros','Loja por loja: venda, m², mix, tamanho, perfil e onda sugerida'),('Divina Logic','5 regras, matriz obrigatório, adaptável e recomendado, e protocolos'),('Regras modulares','12 quadros, em módulos'),('Planogramas v1','Códigos e conteúdo por nível: Empório 1 a 4, Creatina, Ômegas, Proteínas, Granel'),('Plano e checklist','24 itens com responsável, prazo e status'),('Painel semanal','Semana 0 e semanas 1 a 12, com comparação ao controle'),('Auditoria','12 critérios, com nota automática'),('Usabilidade','Roteiro de 6 tarefas e matriz de correções'),('Entregáveis','As 10 frentes do escopo, item por item'),('Cronograma','Marcos de novembro de 2026 a julho de 2027'),('Dados pedidos','O que a rede precisa enviar até 20/11')]
for i,(a,b) in enumerate(IDX,4):
    ws.cell(row=i,column=1,value=a).font=Font(bold=True,color=TER);ws.cell(row=i,column=1).hyperlink=f"#'{a}'!A1";ws.cell(row=i,column=2,value=b)
ws.cell(row=21,column=1,value='Limites').font=Font(bold=True,color=CHO)
for i,t in enumerate(['A base de vendas cobre 71 lojas. Faltam 11, cerca de 27% do faturamento médio: Belém Plaza, Itajaí, Capão da Canoa, Iguatemi, Santa Cruz, Xangri-Lá, Xangri-Lá Max, Holambra, São José dos Campos, Bauru e Francisco Beltrão.','Setores e blocos de empório foram sugeridos por regra de texto sobre a descrição do produto. Cerca de 12% da venda segue a classificar.','A base não tem custo nem cupom: margem e frequência não foram calculadas. Preço médio é valor dividido por quantidade, não tabela.','Marcas em “a cotar” são sugestão de planejamento: nenhum fornecedor foi contatado. Metas são hipótese, a calibrar na semana 0.'],22):
    ws.cell(row=i,column=2,value=t).alignment=Alignment(wrap_text=True,vertical='top')
# árvore
T=df.valor.sum();pct=(df.groupby('setorf').valor.sum()/T*100).to_dict()
A=[('Cuidar','Categoria','Proteínas','Proteínas','Proteínas','Destino','Whey · Beef · Albumina · Colágeno · Veganas','Proteína em pó, por objetivo e digestão',['Proteínas']),
('Cuidar','Categoria','Colágeno & Beleza','Colágeno','Colágeno e Beleza','Destino','Beleza · Articular · Ativos e fórmulas','Colágeno e ativos de pele, cabelo e articulação',['Colágeno e Beleza']),
('Cuidar','Categoria','Vitaminas de A a Z','A a Z','Vitaminas de A a Z','Rotina','Multi · Isoladas · Minerais','Toda a linha de vitaminas e minerais, em ordem encontrável',['Vitaminas de A a Z']),
('Cuidar','Categoria','Ômegas','Ômegas','Ômegas','Rotina','Ômega 3 e DHA · Vegetais · Complementares','Óleos e fórmulas, com régua de uso',['Ômegas']),
('Cuidar','Categoria','Creatina','Creatina','Creatina','Destino','Mais vendidas · Demais marcas · Formatos práticos','Uma casa só. Gummies têm prateleira própria',['Creatina']),
('Cuidar','Categoria','Performance','Performance','Performance','Destino','Antes · Durante · Depois · Acessórios','Treino e reposição',['Performance']),
('Abastecer','Categoria','Chás','Chás','Chás','Rotina','Relaxar · Digestivo · Energia e sabor · Presenteáveis','Chá em caixa. O granel fica no Granel',['Chás']),
('Cuidar','Benefício','Equilíbrio & Bem-Estar','Bem-Estar','Equilíbrio & Bem-Estar','Destino','Foco · Calma · Sono','Sem citar insônia, ansiedade ou estresse',['Equilíbrio e Bem-Estar']),
('Cuidar','Benefício','Saúde Intestinal','Intestino','Saúde Intestinal','Rotina','Probióticos · Prebióticos e fibras · Enzimas · Complementares','Equilíbrio do intestino',['Saúde Intestinal']),
('Cuidar','Benefício','Imunidade','Imunidade','Imunidade','Sazonal','Colmeia · Fitoterápicos · Curva A de C, D e zinco','Sem citar gripe, vírus ou infecção',['Imunidade']),
('Cuidar','Benefício','Peso & Composição','Peso','Peso & Composição','Destino','Saciedade · Metabolismo · Substitutos','Sem promessa de emagrecimento',['Peso e Composição']),
('Cuidar','Fase de vida','Longevidade Saudável','Longevidade','Longevidade Saudável','Destino consultivo','Mulher · Homem · Antioxidantes','Atendimento consultivo',['Longevidade']),
('Cuidar','Fase de vida','Kids','Kids','Kids','Rotina','Suplementos · Café da manhã · Lanches','Linha infantil só aqui',['Kids']),
('Abastecer','Restrição','Sem Glúten','Sem Glúten','Sem Glúten','Destino','Farinhas · Pães e prontos · Biscoitos · Complementares','Nada com glúten, com separação física. Restrição vira atributo nos demais setores',[]),
('Abastecer','Despensa','Granel','Granel','Granel Divina','Rotina','Castanhas · Frutas · Sementes · Snacks','Parede de 20 tubos e prova',['Granel']),
('Abastecer','Despensa','Despensa Saudável (novo, do antigo Gourmet)','Despensa','Despensa Saudável','Rotina','Café da manhã · Lanches · Básicos · Doces sem açúcar · Cafés funcionais · Barras e Snacks','O dia a dia, com selos claros',['Barras e snacks','Café e cápsulas','Farinhas e despensa','Despensa sem setor']),
('Celebrar','Despensa','Empório (novo, do antigo Gourmet)','Empório','Empório Divina Terra','Destino e ocasião','À mesa · Para receber · Do mundo · Adega','Iguarias curadas para receber, cozinhar e presentear',[k for k in pct if k.startswith('Empório')])]
lin=[[a,b,c,d,e,f,g,h,round(sum(pct.get(k,0) for k in ks),2) if ks else None] for a,b,c,d,e,f,g,h,ks in A]
ws=aba('Árvore e naming','Árvore mestre, naming e glossário','Hierarquia: Setor > Categoria > Subcategoria > Segmento > Tipo. Sem Glúten: tamanho a medir, porque a base mistura restrição e produto. Nomes sujeitos a aprovação.',['Motor','Zona da rede','Setor','Nome de placa','Nome oficial','Papel','Prateleiras (subcategorias)','Glossário e regra','% da venda (1ª passada)'],lin,[11,13,34,15,26,16,48,50,12],{9:'0.0'})
# de-para
g=df.groupby(['sku','desc','marca','depto','setorf']).agg(v=('valor','sum'),q=('qtd','sum'),l=('loja','nunique')).reset_index().sort_values('v',ascending=False)
g['c']=g.v.cumsum()/g.v.sum();g['curva']=np.where(g.c<=.8,'A',np.where(g.c<=.95,'B','C'))
cat=prod.set_index('sku').catc.to_dict()
MOT={'Granel':'Abastecer','Barras e snacks':'Abastecer','Café e cápsulas':'Abastecer','Farinhas e despensa':'Abastecer','Despensa sem setor':'Abastecer','Chás':'Abastecer','Café da loja':'Café da loja','Fora de setor':'Fora'}
def motor(s): return 'Celebrar' if s.startswith('Empório') else MOT.get(s,'Cuidar')
def acao(r):
    if r.curva=='A':return 'Manter no núcleo'
    if r.curva=='C' and r.l<=3 and r.v<600:return 'Revisar saída'
    if r.curva=='C':return 'Revisar no ritual mensal'
    return 'Manter por quadro'
lin=[[r.sku,r.desc,r.marca,r.depto,cat.get(r.sku,''),r.setorf,motor(r.setorf),r.curva,round(r.v,2),round(r.q,1),r.l,round(r.v/r.q,2) if r.q else None,acao(r)] for r in g.itertuples()]
aba('De-para de SKUs','De-para de cadastro: SKUs com venda em 13 meses','Setor sugerido por regra de texto. Validar com compras antes de carregar no ERP. Nenhum corte é automático: aplicar as 3 perguntas (frequência, cesta, substituto).',['SKU','Descrição','Marca','Departamento atual','Categoria no ERP','Setor sugerido','Motor','Curva','Venda 13 meses (R$)','Unidades','Lojas','Preço médio (R$)','Ação sugerida'],lin,[9,52,22,24,20,30,11,7,14,10,7,10,24],{9:R,10:'#,##0.0',12:'#,##0.00'})
# empório
e=df[df.bloco.notna()].groupby(['bloco','sku','desc','marca']).agg(v=('valor','sum'),q=('qtd','sum'),l=('loja','nunique')).reset_index().sort_values(['bloco','v'],ascending=[True,False])
lin=[[r.bloco,'Já vende',r.sku,r.desc,r.marca,round(r.v),r.l,'Avaliar no filtro de curadoria'] for r in e.groupby('bloco').head(25).itertuples()]
vend=set(df.sku)
MAP={'Massas e risotos':r'DE CECCO|BARILLA|LA PASTINA.*(MASSA|MACARRAO|PENNE)','Molhos e condimentos':r'MUTTI|KIKKOMAN|SAKURA|BARILLA.*(ARRABB|BASIL|PESTO|MOLHO)','Conservas e antepastos':r'LA PASTINA|ZACCARON','Azeites e vinagres':r'ANDORINHA|PROSPERATO|BORGES AZEITE|VERDE LOURO AZEITE','Chocolates e doces finos':r'LINDT|RITTER|LOTUS BISCOFF|MILKA','Vinhos e espumantes':r'CASA VALDUGA|MIOLO|SALTON|AURORA ESPUMANTE'}
for b,rx in MAP.items():
    a=prod[prod.descc.str.upper().str.contains(rx,regex=True)&~prod.sku.isin(vend)]
    lin+=[[b,'Parado no cadastro',r.sku,r.descc,r.marcac,0,0,'Conferir fornecedor e ativar, se passar no filtro'] for r in a.head(35).itertuples()]
COT=[('Azeites e vinagres','Olivas do Sul; Esporão','R$ 40 a R$ 180. Exigir laudo do fornecedor'),('Massas e risotos','Rummo; Garofalo','R$ 18 a R$ 60'),('Molhos e condimentos','Cirio; pestos italianos','R$ 15 a R$ 50'),('Conservas e antepastos','Azeitonas, alcachofra e tomate seco em vidro','Vidro nos níveis baixos'),('Chocolates e doces finos','Origem brasileira; importados de mesa','R$ 15 a R$ 70'),('Cafés especiais','Torrefações regionais','Cota local de 20%'),('Vinhos e espumantes','Gin Vitória Régia; Emiliana orgânico; Cave Geisse; zero álcool','Acima de R$ 50, 12 a 24 rótulos. Validar licença'),('Queijos','Curados de longa validade com inspeção oficial','Só depois da semana 7, na geladeira existente, seguindo o rótulo'),('Do mundo','Taybe e produtos árabes; molhos e massas asiáticas; saudáveis importados da lista de Francine','Só com 3 módulos ou mais. Rótulo em português e importador identificado'),('Presentes','Latas Haoma; cestas por faixa: até R$ 59,90; R$ 79 a R$ 119; R$ 149 a R$ 199; R$ 249 ou mais','Montar 4 semanas antes da data')]
lin+=[[b,'A cotar','',m,'',None,None,r] for b,m,r in COT]
aba('Empório lista','Empório: SKUs por bloco','Marcas “a cotar” são sugestão, sem contato feito. Faixas de preço: hipótese para a cotação.',['Bloco','Situação','SKU','Produto','Marca','Venda 13 meses (R$)','Lojas','Próximo passo ou regra'],lin,[26,18,9,58,24,12,7,48],{6:R})
# preço
top=g[(g.depto!='A GRANEL')&(g.l>=50)].sort_values('q',ascending=False)
kvi=g[(g.depto!='A GRANEL')&(g.l>=50)&(g.setorf.isin(['Proteínas','Creatina','Ômegas','Vitaminas de A a Z','Colágeno e Beleza','Café e cápsulas','Equilíbrio e Bem-Estar','Longevidade']))].sort_values('v',ascending=False).head(50)
lin=[[r.sku,r.desc,r.marca,r.setorf,round(r.v),r.l,round(r.v/r.q,2),None,None,None,None,None,None] for r in kvi.itertuples()]
aba('Preço de referência','Lista de preço de referência: 50 candidatos','Maiores vendas em setores comparáveis, presentes em 50 ou mais lojas. Preencher a pesquisa mensal por praça. O teto depende do custo, que a rede ainda vai enviar.',['SKU','Descrição','Marca','Setor','Venda 13 meses (R$)','Lojas','Preço médio realizado (R$)','Farmácia 1','Farmácia 2','Farmácia 3','Mercado 1','Mercado 2','Preço-teto da rede'],lin,[9,48,22,22,12,7,12,10,10,10,10,10,10],{5:R,7:'#,##0.00'})
# marcas
bm=BM.sort_values('v',ascending=False).reset_index()
AC={'Núcleo':'Plano anual de negócios','Apoio':'Manter e revisar por setor','Revisar':'Levar ao comitê','Local (até 3 lojas)':'Entra na cota local de 20%'}
lin=[[r.marca,r.tier,round(r.v),round(r.v/bm.v.sum()*100,3),r.l,r.sk,'Sim' if r.v<3000 else 'Não',AC[r.tier] if r.v>=3000 else 'Candidata à 1ª rodada de saída: conferir contrato e estoque'] for r in bm.itertuples()]
aba('Marcas peneira','Peneira de marcas','Base: 11/2025 a 09/2026. Núcleo: 0,5% ou mais da venda. Apoio: 30% ou mais das lojas. Local: até 3 lojas. Corte final é decisão de compras.',['Marca','Faixa','Venda 11 meses (R$)','% da venda','Lojas','SKUs','Menos de R$ 3 mil?','Ação sugerida'],lin,[30,20,14,9,7,7,11,54],{3:R,4:'0.00'})
# lojas
O2={'DT SAO LEOPOLDO','DT CAXIAS','DT SAO MIGUEL','DT CAMPO BOM','DT TRAMANDAI','DT VITORIA','DT VILA MADALENA'}
PIL={'DT PINHEIROS':'Onda 1 (piloto)','DT ALPHAVILLE':'Onda 1 (piloto)','DT MOINHOS - POA':'Controle','DT SINOP':'Controle','DT CAMPOS GOYTACAZES':'Controle reserva'}
X=L.copy();X['tam']=LC.tam;X['perfil']=LC.perfil
lin=[]
for l,r in X.sort_values('media_mes',ascending=False).iterrows():
    on=PIL.get(l,'Onda 2' if l in O2 else 'Onda 3')
    lin.append([l,r.uf,None if pd.isna(r.m2) else float(r.m2),round(r.media_mes),int(r.meses),None if pd.isna(r.rs_m2_mes) else round(r.rs_m2_mes),round(r.sup,1),round(r.gra,1),round(r.gou,1),round(r.empuro,1),int(r.skus),r.tam if isinstance(r.tam,str) else 'Dados insuficientes',r.perfil if isinstance(r.perfil,str) else 'Dados insuficientes',on])
for n in ['Belém Plaza','Itajaí','Capão da Canoa','Iguatemi','Santa Cruz','Xangri-Lá','Xangri-Lá Max','Holambra','São José dos Campos','Bauru','Francisco Beltrão']:
    lin.append(['DT '+n,None,None,None,0,None,None,None,None,None,None,'Fora da base','Fora da base','Onda 2' if n=='Holambra' else 'Definir com a venda'])
aba('Lojas e quadros','Lojas: mix, tamanho, perfil e onda','Base: média de 11/2025 a 09/2026. Tamanho por m² da lista: a contagem de módulos decide. Empório: classificação da 75 LAB. 11 lojas sem venda na base.',['Loja','UF','M² (lista)','Venda média por mês (R$)','Meses na base','R$ por m²','% Suplemento','% Granel','% Gourmet','% Empório','SKUs ativos','Tamanho','Perfil','Onda sugerida'],lin,[28,6,9,13,8,9,10,8,9,9,8,18,18,18],{4:R,6:R})
# Divina Logic
OAR=[('Regra','Um setor por gôndola, uma subcategoria por prateleira',''),('Regra','Primeiro o motivo de compra; a marca vem dentro dele',''),('Regra','Nos olhos, o que mais gira; embaixo, o que pesa',''),('Regra','Um produto, uma casa; ponto extra tem prazo',''),('Regra','Faltou? Puxa o vizinho e registra; não deixa buraco','')]
OAR+=[('Obrigatório',x,'Franqueadora') for x in ['Árvore de setores e nomes de placa','Ordem de leitura de cada setor','Núcleo de SKUs do quadro da loja','Preço-teto da lista de referência','Testeira, régua e etiqueta padrão','Sem Glúten fisicamente separado','Linha Kids só em Kids','Sem frase de cura em nenhuma peça']]
OAR+=[('Adaptável',x,'Franqueado, dentro da regra') for x in ['Número de módulos de cada setor','Até 20% de marcas locais','2 tubos livres no granel','Profundidade por marca dentro da subcategoria','Posição do Empório na planta da loja','Bloco Do mundo, a partir de 3 módulos','Datas regionais no calendário']]
OAR+=[('Recomendado',x,'Franqueado') for x in ['Mesa de Empório no vão central','Potinho de prova no granel','Café servido do que está à venda','Degustação quinzenal','Lousa com a dica da semana','Cross de receita: massa, molho e azeite','Foto semanal no grupo do consultor']]
OAR+=[('Protocolo: ruptura','Puxa o vizinho do mesmo bloco, coloca etiqueta “em reposição” e registra. Sem buraco por mais de 2 dias','Loja'),('Protocolo: novidade','Entra pela faixa de lançamentos por 60 dias. Se girar, ganha casa e tira alguém','Comitê e loja'),('Protocolo: alteração de mix','Só com nova versão publicada, comunicada pelo consultor. Nada de orientação paralela','Franqueadora'),('Protocolo: novo SKU','Novo produto > passa no filtro > classifica na árvore > define prioridade > quem sai? > posiciona > atualiza versão','Comitê'),('Filtro de curadoria','1. Combina com quem se cuida? 2. Só existe bem na curadoria? 3. Tem ocasião clara? 4. A loja consegue operar?','Comitê')]
aba('Divina Logic','Divina Logic: regras, liberdade e protocolos','Padrão sem engessamento.',['Tipo','Item','Quem responde'],[list(x) for x in OAR],[26,100,28])
# modular
TAM={'P':('Até 50 m²',14,3,1,1,36),'M':('50 a 80 m²',28,5,1,2,68),'G':('80 a 120 m²',39,6,2,3,96),'GG':('Acima de 120 m²',53,8,2,4,130)}
PER={'Suplemento forte':(.65,0),'Equilibrado':(.55,0),'Granel forte':(.5,1)}
C2=pd.crosstab(LC.tam,LC.perfil)
lin=[]
for t,(n,tot,gr,ch,em,sk) in TAM.items():
    for p,(f,x) in PER.items():
        g2=gr+x;res=tot-g2-ch-em;su=round(res*f);lin.append([t,n,p,int(C2.loc[t,p]),tot,su,res-su,g2,ch,em,sk,'; '.join(s.replace('DT ','').title() for s in LC[(LC.tam==t)&(LC.perfil==p)].sort_values('media_mes',ascending=False).index[:6])])
aba('Regras modulares','12 quadros de tamanho e perfil, em módulos de 0,90 m','Estimativa a partir das plantas. Gôndola convertida em módulos. Frio, café e caixa fora da conta. A contagem real da loja decide.',['Tamanho','Faixa','Perfil','Lojas hoje','Total de módulos','Cuidar','Abastecer','Granel','Chás','Empório','SKUs de empório','Exemplos'],lin,[9,17,18,8,9,8,10,8,6,9,9,70])
# planogramas
sys.path.insert(0,'fonte')
import graficos as G
lin=[]
NOM={'DN-EMP-M1-v1.0':(G.M1,'Empório','Quadros P'),}
def add(cod,mod,niveis,q):
    for i,row in enumerate(niveis,1):
        for b,f in row: lin.append([cod,q,mod,i,b,f])
add('DN-EMP-M1-v1.0','Empório',G.M1,'P')
for c,ms,nm,q in (('DN-EMP-M2-v1.0',G.M2,['À mesa, na cozinha','Para receber e presentear'],'M'),('DN-EMP-M3-v1.0',G.M3,['À mesa, na cozinha','Para receber e presentear','Do mundo'],'G'),('DN-EMP-M4-v1.0',G.M4,['À mesa, na cozinha','Para receber e presentear','Do mundo','Adega e presentes'],'GG')):
    for m,n in zip(ms,nm): add(c,n,m,q)
for s,c in (('Creatina','DN-CRE-v1.0'),('Ômegas','DN-OME-v1.0'),('Proteínas','DN-PRO-v1.0')):
    t=g[g.setorf==s].head(20)
    for i,r in enumerate(t.itertuples(),1): lin.append([c,'Todos',s,(i-1)//5+1,r.desc,None])
GR=g[g.depto=='A GRANEL'].head(20)
for i,r in enumerate(GR.itertuples(),1): lin.append(['DN-GRA-20-v1.0','Todos','Granel, 20 tubos',i,r.desc,None])
aba('Planogramas v1','Biblioteca de planogramas, versão 1','Código: programa, setor, módulos e versão. Níveis de cima para baixo. Frentes estimadas, a confirmar com a trena. Suplementos em ordem de venda da rede; a versão com frentes fecha depois da trena. Publicação: 18/12/2026.',['Código','Quadro','Módulo ou setor','Nível (tubo, no granel)','Bloco ou produto','Frentes'],lin,[18,8,28,10,60,8])
# plano
PL=[('Preparar','Aprovar posição, motores e pilotos','Diretoria e Francine','09/11/2026'),('Preparar','Instalar o comitê de curadoria','Francine','13/11/2026'),('Preparar','Enviar 11 lojas, cupom, custo e planta de Alphaville','Divina Terra','20/11/2026'),('Preparar','Visitar Alphaville, Perdizes e Hortisabor','75 LAB e Francine','20/11/2026'),('Preparar','Medir Pinheiros e Alphaville com trena','75 LAB','27/11/2026'),('Preparar','Validar árvore e de-para com compras','Gerente de compras e 75 LAB','27/11/2026'),('Preparar','Cotar 3 fornecedores por bloco','Gerente de compras e comitê','04/12/2026'),('Preparar','Consultar jurídico sobre vinho e queijo','Divina Terra','20/11/2026'),('Montar','Foto de antes: 20 pontos fixos','75 LAB e loja','08/01/2027'),('Montar','Fechar a semana 0: venda, tempo de busca, itens errados','75 LAB','15/01/2027'),('Montar','Produzir placas, faixas e etiquetas','Divina Terra (fora do escopo de R$ 29.900)','13/01/2027'),('Montar','Receber o enxoval e conferir validade','Loja e compras','13/01/2027'),('Montar','Treinar a equipe: 2 horas, com o guia rápido','75 LAB e consultor','14/01/2027'),('Montar','Conferir as prateleiras que recebem vidro','75 LAB e loja','14/01/2027'),('Montar','Remanejar produtos fora do horário: 2 noites','Loja, com a 75 LAB','16/01/2027'),('Montar','Foto de depois e checklist da loja','75 LAB','17/01/2027'),('Acompanhar','Atualizar o painel toda segunda','Loja e ERP','Semanal, de 18/01/2027'),('Acompanhar','Foto semanal da gôndola com o consultor','Loja','Semanal'),('Acompanhar','Reunião quinzenal do comitê','Comitê','Quinzenal'),('Acompanhar','Auditoria nas semanas 2, 6 e 10','Consultor','S2, S6, S10'),('Acompanhar','Teste de usabilidade na semana 4','75 LAB','S4'),('Acompanhar','Leitura da semana 6 e virada de fase','75 LAB e diretoria','01/03/2027'),('Acompanhar','Leitura da semana 12 e decisão','75 LAB e diretoria','12/04/2027'),('Acompanhar','Relatório de aprendizados e ajustes','75 LAB','23/04/2027')]
ws=aba('Plano e checklist','Plano e checklist de implantação','Teste de Natal, à parte: ponta em Pinheiros e Alphaville, de 30/11 a 24/12/2026, com itens já da rede.',['Fase','Item','Responsável','Prazo','Status','Observação'],[[a,b,c,d,'A fazer',None] for a,b,c,d in PL],[13,58,38,22,12,40])
dv=DataValidation(type='list',formula1='"A fazer,Em andamento,Feito,Bloqueado"');ws.add_data_validation(dv);dv.add(f'E5:E{4+len(PL)}')
# painel
ws=wb.create_sheet('Painel semanal');ws.sheet_view.showGridLines=False
ws['A1']='Painel semanal do piloto';ws['A1'].font=Font(size=16,bold=True,color=CHO)
ws['A2']='Preencher as células em branco toda segunda. A semana 0 parte da média de 11/2025 a 09/2026. Metas: hipótese, a calibrar na semana 0.';ws['A2'].font=Font(size=10,italic=True,color='6F5F55')
B={'Pinheiros':('DT PINHEIROS'),'Moinhos (controle)':('DT MOINHOS - POA'),'Alphaville':('DT ALPHAVILLE'),'Sinop (controle)':('DT SINOP')}
KP=[('Venda da semana (R$)','media_mes',lambda v:round(v/4.33),'+3 p.p. sobre o controle'),('Venda de suplemento (R$)','sup_abs',lambda v:round(v/4.33),'Sem queda maior que o controle'),('Venda de granel (R$)','gra_abs',lambda v:round(v/4.33),'+3 p.p. de participação'),('Venda de empório (R$)','emp_abs',lambda v:round(v/4.33),'6% ou mais da venda'),('Módulos de empório instalados',None,None,'3 em Pinheiros, 2 em Alphaville'),('Cupons',None,None,''),('Itens por cupom',None,None,'+0,3'),('Tíquete médio (R$)',None,None,''),('Ruptura no empório (SKUs)',None,None,''),('Perda por validade (R$)',None,None,'Até 2% da venda do empório')]
row=4
for loja,k in B.items():
    r=L.loc[k]
    base={'media_mes':r.media_mes,'sup_abs':r.media_mes*r.sup/100,'gra_abs':r.media_mes*r.gra/100,'emp_abs':r.media_mes*r.empuro/100}
    ws.cell(row=row,column=1,value=loja).font=Font(bold=True,size=13,color=CHO);row+=1
    cab=['Indicador','Meta, S12','S0 (base por semana)']+[f'S{i}' for i in range(1,13)]
    for j,c in enumerate(cab,1):
        x=ws.cell(row=row,column=j,value=c);x.font=Font(bold=True,color='FFFFFF');x.fill=PatternFill('solid',fgColor=TER)
    head=row;row+=1;first=row
    for nome,campo,f,meta in KP:
        ws.cell(row=row,column=1,value=nome);ws.cell(row=row,column=2,value=meta if 'controle' not in loja else '')
        if campo:
            ws.cell(row=row,column=3,value=f(base[campo])).number_format=R
        row+=1
    for nome,idx in (('% Suplemento',1),('% Granel',2),('% Empório',3)):
        ws.cell(row=row,column=1,value=nome).font=Font(italic=True)
        for c in range(3,16):
            L_=CL(c);ws.cell(row=row,column=c,value=f'=IF(N({L_}{first})=0,"",{L_}{first+idx}/{L_}{first}*100)').number_format='0.0'
        row+=1
    if 'controle' not in loja:
        ws.cell(row=row,column=1,value='Venda de empório por módulo, em 4,33 semanas (R$)').font=Font(italic=True)
        for c in range(4,16):
            L_=CL(c);ws.cell(row=row,column=c,value=f'=IF(N({L_}{first+4})=0,"",{L_}{first+3}/{L_}{first+4}*4.33)').number_format=R
        ws.cell(row=row,column=2,value='R$ 4 mil ou mais');row+=1
    row+=1
ws.cell(row=row,column=1,value='Teste contra o controle').font=Font(bold=True,size=13,color=CHO);row+=1
for nome,a,b in (('Pinheiros menos Moinhos: variação sobre S0, em p.p.',6,6+18),('Alphaville menos Sinop: variação sobre S0, em p.p.',6+18+15,6+18+15+18)): pass
ws.column_dimensions['A'].width=46;ws.column_dimensions['B'].width=30;ws.column_dimensions['C'].width=14
for c in range(4,16): ws.column_dimensions[CL(c)].width=10
ws.cell(row=row,column=1,value='Regra: comparar a variação da loja sobre a própria S0 com a variação do controle no mesmo período. Vai para a rede, ajusta ou para: critérios na tela “Como decidir”.')
# auditoria
Crit=['Setor e subcategoria com placa correta','Produto no setor certo','Ordem de leitura respeitada','Nível dos olhos com o que mais gira','Núcleo de SKUs presente','Ruptura tratada, sem buraco','Preço visível e no padrão','Curva A no preço de referência','Peças instaladas e atualizadas','Sem frase de cura nem material fora do padrão','Granel limpo e tubo acima de 1/3','Empório com validade e versão do planograma em dia']
ws=aba('Auditoria','Checklist de auditoria','Responder OK, AJUSTAR ou NSA. Evidência: 6 fotos fixas. 85% ou mais: loja no padrão. 70% a 84%: correção em 15 dias. Abaixo de 70%: visita em 7 dias.',['#','Critério','S2 Pinheiros','S6 Pinheiros','S10 Pinheiros','S2 Alphaville','S6 Alphaville','S10 Alphaville'],[[i+1,c,None,None,None,None,None,None] for i,c in enumerate(Crit)],[5,54,12,12,12,12,12,12])
dv=DataValidation(type='list',formula1='"OK,AJUSTAR,NSA"');ws.add_data_validation(dv);dv.add('C5:H16')
ws.cell(row=17,column=2,value='Nota').font=Font(bold=True)
for c in range(3,9):
    L_=CL(c);ws.cell(row=17,column=c,value=f'=IF(COUNTIF({L_}5:{L_}16,"OK")+COUNTIF({L_}5:{L_}16,"AJUSTAR")=0,"",COUNTIF({L_}5:{L_}16,"OK")/(COUNTIF({L_}5:{L_}16,"OK")+COUNTIF({L_}5:{L_}16,"AJUSTAR")))').number_format='0%'
ws.auto_filter.ref=None
# usabilidade
U=[('Localizar uma categoria','“Onde fica a creatina?” Da porta, sem perguntar','30 s'),('Colocar um produto novo','“Chegou um azeite novo. Onde ele entra?”, com a árvore de decisão','2 min'),('Ler um planograma','Explicar um módulo de empório usando a ficha','3 min'),('Corrigir uma exposição errada','Módulo montado com 5 erros. Achar e arrumar','5 min'),('Tratar uma ruptura','Sumiu o Crealift. O que fazer, sem deixar buraco?','3 min'),('Adaptar a loja menor','Reorganizar uma prateleira com menos produtos','10 min')]
aba('Usabilidade','Teste de usabilidade, semana 4','Quem testa: 2 colaboradores novos e 1 gerente de outra loja. Critério: 5 de 6 tarefas no tempo, sem ajuda da equipe central.',['Tarefa','Roteiro','Tempo-limite','Pessoa 1: tempo','Pessoa 2: tempo','Pessoa 3: tempo','Dúvida registrada','Correção decidida','Dono','Prazo'],[[a,b,c,None,None,None,None,None,None,None] for a,b,c in U],[30,56,10,10,10,10,34,34,14,12])
# entregáveis
E=[('1 Diagnóstico',[('Imersão na loja piloto','Entregue'),('Diagnóstico fotográfico','Entregue'),('Mapa AS IS','Entregue'),('Inventário de categorias e mobiliários','Entregue'),('Alphaville','Piloto')]),('2 Estratégia de categorias',[('Árvore de categorias','V1'),('Hierarquia','V1'),('Critérios de classificação','V1'),('Naming das categorias-chave','V1'),('Glossário','V1'),('De-para do cadastro validado','18/12/2026')]),('3 Divina Logic',[('Princípios de exposição','V1'),('Regras universais','V1'),('Matriz obrigatório, adaptável, recomendado','V1'),('Protocolos de ruptura, novidade e mix','V1'),('Documento Divina Logic','18/12/2026')]),('4 Planogramas',[('Regras modulares','V1'),('Ficha de interpretação','V1'),('Sistema de versionamento','V1'),('Biblioteca de planogramas-base','18/12/2026'),('Aplicados às categorias definidas','18/12/2026')]),('5 Sistema visual',[('Conceito e categorias','V1'),('Comunicação de benefícios','V1'),('Regras de utilização','V1'),('Aplicações simuladas','V1'),('Testeiras e templates finais','18/12/2026')]),('6 Loja piloto',[('Plano de implantação','V1'),('Checklist de execução','V1'),('Aplicação completa','Piloto'),('Acompanhamento','Piloto'),('Antes e depois','Piloto'),('Relatório de ajustes','Piloto')]),('7 Manualização',[('Checklists','V1'),('Guia Rápido, primeira versão','Piloto'),('Manual Digital Divina Navegação','Abr a mai/2027'),('FAQ inicial','Abr a mai/2027'),('Versão editável','Abr a mai/2027')]),('8 Treinamento',[('Trilha e estrutura','V1'),('Treino da equipe do piloto','Piloto'),('Apresentação, exercícios e quiz','Abr a mai/2027'),('Material de apoio e sessão','Abr a mai/2027')]),('9 Clusterização',[('Definição de clusters','V1'),('Regras por tamanho e perfil','V1'),('Exemplos de adaptação','V1'),('Contagem final em módulos','Abr a mai/2027')]),('10 Rollout e controle',[('Plano de implantação na rede','V1'),('Checklist de auditoria','V1'),('Governança e versionamento','V1'),('Janela de suporte','Abr a mai/2027')]),('Novo: reposicionamento',[('Posição e motores','V1'),('Filtro de curadoria','V1'),('Lista de SKUs de empório','V1'),('Painel de performance','V1'),('Limpeza de marcas, 1ª lista','V1'),('Calendário de trade','V1'),('Lista final do empório','18/12/2026')])]
aba('Entregáveis','Matriz de entregáveis','V1: nesta apresentação e neste kit. Prazos condicionados aos dados e às aprovações.',['Frente','Item','Estágio'],[[f,i,s] for f,it in E for i,s in it],[28,50,18])
aba('Cronograma','Marcos do projeto','',['Marco','Início','Fim'],[['Decisões e dados','09/11/2026','20/11/2026'],['Visitas e trena','09/11/2026','27/11/2026'],['Árvore, de-para e cotação','16/11/2026','11/12/2026'],['Ponta de Natal (teste)','30/11/2026','24/12/2026'],['Planograma-base e Divina Logic','','18/12/2026'],['Preparar piloto','04/01/2027','17/01/2027'],['Piloto: fase 1','18/01/2027','28/02/2027'],['Piloto: fase 2','01/03/2027','11/04/2027'],['Manual, guia e treinamento','13/04/2027','15/05/2027'],['Onda 2 (8 lojas)','17/05/2027','11/07/2027'],['Onda 3 (rede)','19/07/2027','em lotes de 10 a 15 lojas por mês']],[38,14,34])
aba('Dados pedidos','O que a rede precisa enviar até 20/11','',['Dado','Para quê','Prioridade'],[['Venda por SKU, loja e mês das 11 lojas fora da base','Fechar quadros, incluir Holambra e as Diamante','Alta'],['Relatório de cupom: itens por cupom, tíquete e frequência','Provar frequência e cesta, base do piloto','Alta'],['Custo e margem por SKU','Preço-teto e rentabilidade','Alta'],['Planta de Alphaville e acesso para a trena','Planograma da loja e conta de módulos','Alta'],['Calendário oficial de trade de 2027','Integrar o calendário proposto','Média'],['Guias de Natal, Páscoa e Dia dos Pais, se existirem','Reaproveitar mecânicas','Média']],[58,50,10])

# ---- receita e calculadoras
import receita as RC
RE=[('1','Entender como ela escolhe','Rede','Árvore de decisão por setor: motivo, tipo, marca, preço. Pedir aos fornecedores e validar com clientes.','ECR Brasil e Sebrae, 2014; Rooderkerk e Lehmann, 2021'),('2','Dar um papel a cada categoria','Rede','Destino, rotina, ocasião ou conveniência. O papel decide espaço, preço e lugar na loja.','Partnering Group e ECR, anos 1990'),('3','Saber que loja é esta','Loja','Contar módulos e ver o perfil de venda: suplemento forte, equilibrado ou granel forte.','Umbrex; DotActiv; adaptação 75 LAB'),('4','Escolher os produtos','Rede e loja','Núcleo igual, lista aprovada, até 20% local. Entra um, sai um.','Kök, Fisher e Vaidyanathan; Kaufmann e Eroglu, 1999'),('5','Dividir o espaço','Loja, com a calculadora','Módulos da loja x venda x peso do papel, conferindo o que cabe. Aba Calc espaço.','Corstjens e Doyle, 1981; Eisend, 2014; pesos da 75 LAB, a calibrar'),('6','Definir as frentes','Loja, com a calculadora','Para não faltar: fórmula da aba Calc frentes. Para ser visto: líder do bloco até 3 frentes.','Patente Walmart adaptada; Chandon e outros, 2009; Drèze e outros, 1994'),('7','Montar pela regra','Loja','Um setor por gôndola, uma subcategoria por prateleira, olhos para o que mais gira, líder no centro, marca em bloco, pesado embaixo, uma casa por produto.','Padrão de setores da rede; Atalay e outros, 2012; Deng e outros, 2016'),('8','Conferir e ajustar','Loja e consultor','Auditoria com foto; ritual mensal de mix; revisão de espaço por trimestre; papéis e tipos por ano.','Umbrex; Vasconcellos e Sampaio, 2009')]
aba('Receita','A receita em 8 passos','Mesma lógica para qualquer loja. Parâmetros numéricos são proposta da 75 LAB, a calibrar no piloto.',['Passo','O que é','Quem faz','Como','Base'],[list(x) for x in RE],[7,30,22,70,50])
# calculadora de espaço, com exemplo editável (Pinheiros)
a=RC.alocar('DT PINHEIROS',30,3)
ws=aba('Calc espaço','Calculadora de espaço, passo 5','Edite as células em amarelo: total de módulos, empório, venda % de cada setor, produtos que fazem 80% e 95%, e quantos cabem no módulo. Exemplo carregado: Pinheiros.',['Setor','Papel','Motor','Venda % (edite)','Peso do papel','Pontos','Módulos pela venda','Produtos que fazem 80%','Produtos que fazem 95%','Cabem por módulo (a medir)','Mínimo','Máximo','Módulos sugeridos'],[],[20,11,11,10,8,9,10,10,10,10,8,8,11])
ws['O4']='Total de módulos (sem granel, frio, café e caixa)';ws['P4']=30;ws['O5']='Módulos de empório (espaço de teste)';ws['P5']=3;ws['O6']='Disponível';ws['P6']='=P4-P5';ws.column_dimensions['O'].width=46
AM=PatternFill('solid',fgColor='F6E7B8')
for c in ('P4','P5'): ws[c].fill=AM
ws['O8']='Peso: Destino';ws['P8']=1.2;ws['O9']='Peso: Rotina';ws['P9']=1.0;ws['O10']='Peso: Ocasião';ws['P10']=0.8;ws['O11']='Peso: Conveniência';ws['P11']=0.7
n=len(a);fim=4+n
for i,r in enumerate(a.itertuples(),5):
    ws.cell(row=i,column=1,value=r.s);ws.cell(row=i,column=2,value=r.pap);ws.cell(row=i,column=3,value=r.mot)
    x=ws.cell(row=i,column=4,value=round(r.pv,1));x.fill=AM
    ws.cell(row=i,column=5,value=f'=IF(B{i}="Destino",$P$8,IF(B{i}="Rotina",$P$9,IF(B{i}="Ocasião",$P$10,$P$11)))')
    ws.cell(row=i,column=6,value=f'=D{i}*E{i}').number_format='0.0'
    ws.cell(row=i,column=7,value=f'=$P$6*F{i}/SUM($F$5:$F${fim})').number_format='0.0'
    for c,v in ((8,r.n80),(9,r.n95),(10,r.cap)):
        y=ws.cell(row=i,column=c,value=int(v));y.fill=AM
    ws.cell(row=i,column=11,value=f'=H{i}*1.25/J{i}').number_format='0.0'
    ws.cell(row=i,column=12,value=f'=I{i}*1.25/J{i}').number_format='0.0'
    ws.cell(row=i,column=13,value=f'=ROUND(MEDIAN(K{i},G{i},L{i})*2,0)/2').number_format='0.0'
ws.cell(row=fim+1,column=1,value='Soma').font=Font(bold=True);ws.cell(row=fim+1,column=13,value=f'=SUM(M5:M{fim})').number_format='0.0'
ws.cell(row=fim+2,column=1,value='Sobra ou falta frente ao disponível: distribuir meio módulo por vez, começando pelo destino').font=Font(italic=True);ws.cell(row=fim+2,column=13,value=f'=P6-M{fim+1}').number_format='0.0'
ws.auto_filter.ref=None
# calculadora de frentes
ws=aba('Calc frentes','Calculadora de frentes, passo 6','Frentes = (venda por semana ÷ 7 × dias até a próxima entrega + segurança) ÷ quantas cabem atrás de uma frente, arredondando para cima. Depois, a regra de visibilidade. Exemplos ilustrativos.',['Produto','Venda por semana','Dias até a próxima entrega','Segurança (unidades)','Cabem atrás de uma frente','Frentes para não faltar','Líder do bloco? (Sim ou Não)','Frentes finais'],[],[42,10,12,10,12,12,14,10])
EXF=[('Líder de creatina em Pinheiros',1.7,21,1,6,'Sim'),('Líder de ômega em Pinheiros',0.6,21,1,6,'Sim'),('Produto de curva B',0.3,21,1,6,'Não')]
for i,(n_,v,dd,sg,cb,lid) in enumerate(EXF+[('',None,21,1,6,'Não')]*12,5):
    ws.cell(row=i,column=1,value=n_ or None).fill=AM
    for c,val in ((2,v),(3,dd),(4,sg),(5,cb),(7,lid)):
        ws.cell(row=i,column=c,value=val).fill=AM
    ws.cell(row=i,column=6,value=f'=IF(N(B{i})=0,"",MAX(1,ROUNDUP((B{i}/7*C{i}+D{i})/E{i},0)))')
    ws.cell(row=i,column=8,value=f'=IF(F{i}="","",IF(G{i}="Sim",MIN(3,MAX(F{i},2)),F{i}))')
ws.auto_filter.ref=None
# espaço por loja
lin=[]
TOT={'P':(11,1),'M':(23,2),'G':(33,3),'GG':(45,4)}
for l,r in LC.sort_values('media_mes',ascending=False).iterrows():
    if r.tam not in TOT: continue
    t,em=(30,3) if l=='DT PINHEIROS' else TOT[r.tam]
    b=RC.alocar(l,t,em).set_index('s').f
    lin.append([l.replace('DT ','').title(),r.tam,r.perfil,t]+[float(b[s[0]]) for s in RC.SET]+[em])
aba('Espaço por loja','Módulos sugeridos por loja, com a venda real','Resultado da receita para 59 lojas. O total de módulos é estimado pelo tamanho da loja: troque pela contagem real na aba Calc espaço. Exclui granel, frio, café e caixa.',['Loja','Tamanho','Perfil','Total de módulos']+[s[0] for s in RC.SET]+['Empório'],lin,[24,8,17,8]+[9]*len(RC.SET)+[8])
ORD=['Leia-me','Receita','Calc espaço','Calc frentes','Espaço por loja'];wb._sheets=[wb[n] for n in ORD]+[x for x in wb._sheets if x.title not in ORD]
ws=wb['Leia-me']
for i,(a_,b_) in enumerate([('Receita','Os 8 passos, quem faz e a base de cada um'),('Calc espaço','Calculadora de módulos por setor, para qualquer loja'),('Calc frentes','Calculadora de frentes por produto'),('Espaço por loja','Resultado da receita para 59 lojas, com venda real')],27):
    ws.cell(row=i,column=1,value=a_).font=Font(bold=True,color=TER);ws.cell(row=i,column=1).hyperlink=f"#'{a_}'!A1";ws.cell(row=i,column=2,value=b_)
ws.cell(row=26,column=1,value='Novas abas').font=Font(bold=True,color=CHO)

pathlib.Path('kit').mkdir(exist_ok=True)
out='kit/Divina-Terra-Kit-de-Execucao-do-Piloto-v1.xlsx';wb.save(out)
print(out,pathlib.Path(out).stat().st_size//1024,'KB',wb.sheetnames)
# confere travessão
bad=0
for ws in wb:
    for row in ws.iter_rows(values_only=True):
        for v in row:
            if isinstance(v,str) and ('—' in v or '–' in v):bad+=1
print('travessoes (incluindo descricoes do ERP):',bad)
print(kvi.head(3)[['desc','v']].to_string())
