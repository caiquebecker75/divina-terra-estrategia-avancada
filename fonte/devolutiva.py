# Gera devolutiva.html: a resposta, ponto a ponto, à devolutiva da rede (documento de 13/11/2026, recebido em 16/11/2026).
# Pedido do item 8.1: consolidar a lista de correções, registrar o que mudou e separar o que depende da Divina Terra.
# Cada ponto diz o que foi feito, em que versão, onde ver e o que ainda precisa da rede. Rodar depois de build.py.
import pathlib, re, html, json
R = pathlib.Path(__file__).resolve().parent.parent
TIT = re.findall(r'<section\b[^>]*data-titulo="([^"]*)"', (R / 'book.html').read_text())

def b(t):
    "Link para a tela do book pelo título."
    return (f'Book: {t}', f'book.html#{TIT.index(t) + 1}')
def m(t, sec):
    return (f'Manual: {t}', f'manual.html#{sec}')
K = ('Planilha de classificação, enviada à parte', None)
X = ('Lista de execução por loja, enviada à parte', None)

# (número, prioridade, tema, o que a rede pediu, o que fizemos, versão: 2 ou 4, onde ver, o que depende da rede)
ITENS = [
 ('02', 'Gestão de categorias e sortimento', [
  ('2.1', 'Crítica', 'Kids e Peso', 'Separar Kids e Peso, revisar produtos, espaço, fichas, planogramas e simulações.',
   'Kids e Peso viraram dois setores, cada um com ficha, espaço e planograma próprios. Na loja pequena, dividem a gôndola de Equilíbrio & Bem-Estar, cada um na sua prateleira.', 2,
   [b('As categorias indicadas'), b('O manual de cada categoria'), m('fichas de categoria', 'gc')], ''),
  ('2.2', 'Crítica', 'Revisão integral dos produtos', 'Auditar todo o mix: categoria, subcategoria, marca, duplicidade, essenciais e regionais; lista com SKU, categoria atual, sugerida e justificativa.',
   'Todos os produtos foram reclassificados pela árvore de 16 setores da própria rede, e os 2.706 que mais vendem foram conferidos um a um. A planilha traz SKU, categoria no sistema, categoria sugerida e justificativa. Na versão 4, mais 49 produtos de higiene e cosmético (Alva, Musa, Guday e outros) saíram de setores de alimento.', 4,
   [K, b('As categorias indicadas')], '2.107 produtos, 1,4% da venda, seguem sem setor claro e estão na planilha para compras indicar.'),
  ('2.3', 'Alta', 'Proteínas', 'Rever whey, vegetais, isoladas, beef, sachês e formatos pela lógica de busca.',
   'Todas as proteínas ficam no mesmo setor, lado a lado, uma prateleira por tipo: whey, proteína do colágeno, beef, veganas e albumina. A vegana fica junto das outras, como alternativa para a mesma necessidade.', 2,
   [m('ficha de Proteínas', 'gc'), b('Planograma da loja M')], ''),
  ('2.4', 'Alta', 'Vitaminas e ômegas', 'Avaliar se ômegas pedem setor próprio ou subcategoria.',
   'Ômegas mantêm setor próprio, colado em Vitaminas: ômegas com coenzima Q10 somam 6,4% da venda, contra 2,6% de vitaminas. Na loja pequena, os dois dividem uma gôndola.', 2,
   [b('As categorias indicadas'), b('A lista de execução de cada loja')], 'Validar com compras se o setor próprio fica.'),
  ('2.5', 'Alta', 'Chás, bebidas e kombuchas', 'Tirar kombucha dos chás e definir critério para caixa, granel e gancheira.',
   'Kombucha saiu de Chás e foi para Geladeira e bebidas prontas, em todas as páginas e na base. Chá em caixa, a granel e de gancheira ficam no setor de Chás, com critério por formato.', 2,
   [m('ficha de Chás', 'gc')], 'Validar a área proposta Geladeira e bebidas prontas.'),
  ('2.6', 'Alta', 'Barrinhas e snacks', 'Rever barras espalhadas e avaliar área própria, com exposição secundária.',
   'Barras e snacks ganharam área própria proposta: 4,1% da venda, e a loja mediana vende 87 produtos da área num trimestre. Caixa e ponta são exposição secundária, com prazo.', 2,
   [b('As categorias indicadas'), m('profundidade do sortimento', 'produtos')], 'Validar a área proposta Barras e snacks.'),
  ('2.7', 'Alta', 'Marca própria Vivea', 'Mais visibilidade: olhos, frentes e comunicação.',
   'Vivea nos olhos, com pelo menos 2 frentes, em todo tamanho de loja, e no aniversário de 16 anos.', 2,
   [b('As regras da prateleira'), b('As campanhas da rede')], ''),
  ('2.8', 'Alta', 'Categorias com sortimento limitado', 'Reavaliar a profundidade em cafés funcionais, snacks, chás, despensa, importados, colágeno, performance, longevidade e vitaminas.',
   'A lista aprovada ficou maior. Na versão 4, uma tabela compara o desenho de cada tamanho de loja com o que a loja mediana vende: em 7 das 8 categorias o desenho cobre a venda. A exceção é Performance, com 27 produtos no desenho M contra 63 vendidos: sachês e géis vão para gancheira ou display de caixa, e o piloto mede.', 4,
   [m('profundidade do sortimento', 'produtos')], ''),
 ]),
 ('03', 'Dados, indicadores e premissas', [
  ('3.1', 'Alta', 'Particularidades regionais', 'Separar nacional, regional e local, por porte, sem generalizar loja específica.',
   'Cada produto ganhou um papel: essencial (nacional), complementar (lista aprovada) e regional (forte só numa região, fica na região dela). As três regiões têm prioridades diferentes, e as lojas de referência aparecem como caso, não como molde.', 2,
   [b('Três redes dentro de uma'), b('Núcleo, lista e local')], ''),
  ('3.2', 'Alta', 'Indicadores e dados', 'Conferir fontes e períodos, chocolate, azeite e preço ilustrativo contra praticado.',
   'Chocolate: o cacau caiu, mas a barra e o bombom subiram 24,8% em 12 meses na prateleira (IPCA). Azeite: de R$ 68 a R$ 108 a garrafa, pelo preço praticado na rede. Toda simulação traz a fonte e o período.', 2,
   [b('Razão 2: as portas abertas'), b('A régua de preço por categoria')], ''),
  ('3.3', 'Alta', 'Critérios de manutenção e exclusão', 'Giro, curva ABC, margem, validade, estoque, ruptura, sazonalidade, perfil, capacidade e novidades.',
   'Na versão 2, regra de entrada e saída. Na versão 4, uma tabela com os dez critérios, o sinal que dispara cada ação (manter, reduzir, tirar ou incluir) e o dado que já temos.', 4,
   [b('Núcleo, lista e local'), m('critérios para manter, reduzir, tirar e incluir', 'produtos')], 'Margem, estoque e perdas dependem de custo, estoque e relatório de perdas por loja.'),
 ]),
 ('04', 'Planograma e exposição', [
  ('4.1', 'Crítica', 'Formatos de loja', 'Diretrizes para lojas pequenas, médias e grandes, sem reforma, com alternativas.',
   'Planogramas P, M e G e 12 tipos de loja (tamanho e perfil). Nada pede obra: régua, faixa e etiqueta nas gôndolas atuais, e alternativa quando o móvel não existe.', 2,
   [b('O sisteminha: 12 quadros'), b('Planograma da loja P'), b('A lista de execução de cada loja')], ''),
  ('4.2', 'Crítica', 'Orientações para execução', 'Por produto: permanece, realoca, reduz, retira, incorpora, reposição, frentes e substituição.',
   'Cada loja recebe a sua lista, produto a produto. Na versão 4 entrou a ação "reduz", com 1 frente na parte local, e Belém Plaza e Holambra ganharam lista própria: são 61 lojas.', 4,
   [b('A lista de execução de cada loja'), X], 'São José dos Campos ainda não tem metragem na lista da rede.'),
  ('4.3', 'Alta', 'Altura e visibilidade', 'Não só volume: impulso, geleia contra vinagre, marca própria, margem e jornada.',
   'Nos olhos, o que mais gira e o que se compra por impulso: geleia acima do vinagre e Vivea nos olhos.', 2,
   [b('As regras da prateleira')], ''),
  ('4.4', 'Alta', 'Revisão das imagens', 'Conferir todos os planogramas e corrigir produtos deslocados.',
   'As imagens foram refeitas a partir da classificação revisada. Na versão 4, um creme de pentear infantil da Alva saiu do planograma de Kids das lojas G.', 4,
   [b('Planograma da loja P'), b('Planograma da loja M'), b('Planograma da loja G')], ''),
  ('4.5', 'Alta', 'Granel na entrada', 'Alternativas para bins na parede, sinalização, percurso e custo, sem reforma.',
   'Nenhum bin sai do lugar: placa suspensa visível da porta, potinho de prova na entrada e ponta com 4 a 6 itens em porção. O custo de cada peça está no book.', 2,
   [b('A lista de execução de cada loja'), b('Custo e tempo por ponto da loja')], ''),
  ('4.6', 'Alta', 'Mesa ou ilha central', 'Avaliar a necessidade, alternativas para loja pequena e teste antes.',
   'Só onde houver vão livre de 2 × 2 m no caminho da cliente; senão, ponta de gôndola do mês. Pinheiros testa e mede antes de ir para outras lojas.', 2,
   [b('A lista de execução de cada loja')], ''),
  ('4.7', 'Alta', 'Preservar a experiência', 'Organização, circulação, setores claros, variedade, curadoria e equilíbrio.',
   'Os seis princípios ficam como regra de toda loja e aparecem na visão para a diretoria como o que não muda.', 2,
   [('Visão para a diretoria: a experiência na loja', 'diretoria.html#12'), m('regras da rede', 'regras')], ''),
 ]),
 ('05', 'Granel e empório Gourmet', [
  ('5.1', 'Crítica', 'Núcleo do granel', 'Rever núcleo e lista aprovada pela curva ABC, sem duplicidade.',
   'Núcleo são os essenciais (curva A e vendidos em mais da metade das lojas); lista aprovada, os complementares (curva A ou B e 20% das lojas); local, os regionais. A lista aprovada cresceu.', 2,
   [b('Núcleo, lista e local'), b('O que entra em cada parte')], ''),
  ('5.2', 'Alta', 'Produtos regionais', 'Brigadeiro regional, frutas perto de vinho, nacional contra local.',
   'O brigadeiro Fit Sweet e a Shark Pro viraram regionais. Fruta seca não aparece mais ao lado do vinho.', 2,
   [b('Núcleo, lista e local'), b('Plano Celebrar')], ''),
  ('5.3', 'Alta', 'Visão ampla do empório', 'Azeites, massas e molhos, geleias, chocolates, conservas, cafés, chás, importados, presentes e ocasiões.',
   'O empório é o setor Gourmet da árvore da rede, com prateleiras de azeites e molhos, massas e prontos, doces e chocolates, cafés, vinhos e presenteáveis, e o calendário por ocasião.', 2,
   [b('Plano Celebrar'), b('Semáforo de vinho, queijo e importados'), b('O que falta no portfólio')], 'O mix final é de compras, com a consultoria que a rede pretende contratar. A 75 LAB leva o Gourmet para a exposição e sugere.'),
  ('5.4', 'Alta', 'Preço dos azeites', 'Conferir marca, volume, SKU e faixa.',
   'A faixa antiga misturava vinagre. Agora é só azeite, pelo preço praticado: de R$ 68 a R$ 108 a garrafa.', 2,
   [b('A régua de preço por categoria')], ''),
  ('5.5', 'Alta', 'Lojas de referência', 'Dados, público, lugar, concorrência e o que se replica.',
   'Vila Madalena virou caso contextualizado. Na versão 3, Holambra entrou como segunda prova (11,9% de Gourmet). Na versão 4, uma tabela de Vila Madalena, Holambra, Alphaville e Pinheiros diz o que vai para a rede e o que fica na loja.', 4,
   [b('Razão 5: a prova na própria rede'), m('lojas de referência', 'produtos')], 'Concorrência ao redor de cada loja: a levantar com a rede.'),
  ('5.6', 'Média', 'Boas práticas no granel', 'Alinhar ao Manual de Boas Práticas e Armazenamento.',
   'O material de trade remete ao manual da rede: higiene, validade e manuseio seguem o manual, sem substituí-lo.', 2,
   [m('ficha de Granel', 'gc')], 'Receber o Manual de Boas Práticas e Armazenamento para conferir exigências locais.'),
 ]),
 ('06', 'Calendário de trade 2027', [
  ('6.1', 'Crítica', 'Calendário da rede', 'Cruzar com a planilha interna e separar campanha, apoio e conteúdo.',
   'Todas as datas seguem a tabela oficial de 2027, com o nível de cada uma: campanha, apoio ao trade, conteúdo ou em aberto.', 2,
   [b('Calendário de trade 2027'), b('Calendário mês a mês')], 'Validar as datas marcadas como em aberto.'),
  ('6.2', 'Crítica', 'Black Friday', 'Protagonismo, abordagem comercial, exposição, vitrine, PDV e cronograma.',
   'Campanha própria, com esquenta, cronograma desde setembro, mecânica, exposição, vitrine e PDV.', 2,
   [b('As campanhas da rede')], 'Escolher a mecânica e negociar a verba com as marcas.'),
  ('6.3', 'Alta', 'Dia do Consumidor e Dia do Cliente', 'Abordagem, mecânicas, PDV e ativação, não lista de mix.',
   'Cada data tem objetivo, cronograma, mecânica para escolher, exposição, vitrine e PDV.', 2,
   [b('As campanhas da rede')], 'Escolher as mecânicas.'),
  ('6.4', 'Alta', 'Aniversário de 16 anos', 'Campanha de 6 de maio dentro de maio.',
   'Semana de aniversário de 3 a 9/05, emendada com o Dia das Mães: 16 produtos com 16%, Vivea e conteúdo institucional.', 2,
   [b('As campanhas da rede')], ''),
  ('6.5', 'Alta', 'Datas não trabalhadas', 'Rever Corpus Christi e separar contexto de campanha.',
   'Corpus Christi saiu. Datas de contexto aparecem como conteúdo ou em aberto, não como campanha.', 2,
   [b('Calendário de trade 2027')], ''),
  ('6.6', 'Alta', 'Datas de conscientização', 'Setembro Amarelo, Outubro Rosa e Novembro Azul sem uso comercial.',
   'As três viraram conteúdo, sem produto vinculado.', 2, [b('Calendário mês a mês')], ''),
  ('6.7', 'Média', 'Datas complementares', 'Dia do Nutricionista, volta às aulas, férias e ocasiões.',
   'Dia do Nutricionista (31/08), volta às aulas em janeiro e julho e férias de dezembro estão no calendário.', 2,
   [b('Calendário de trade 2027')], ''),
 ]),
 ('08', 'Implantação', [
  ('8.1', 'Alta', 'Governança das revisões', 'Lista de correções, pontos da rede, registro, versões e nova apresentação.',
   'Cada entrega é uma versão guardada, com o que mudou. Esta página consolida todas as correções e separa o que depende da Divina Terra. A visão para a diretoria é a apresentação de validação.', 4,
   [('Versões anteriores', 'versoes/'), ('Visão para a diretoria', 'diretoria.html')], ''),
 ]),
]

# Seção 07: página a página (páginas do book da versão 1)
PAGS = [
 ('9', 'Posicionamento', 'Virou “O empório para quem quer se cuidar”: convida também quem está começando.', [b('A posição em uma frase')]),
 ('15', 'Linguagem nutricional', 'Saiu a ideia de permissão: a saúde é a porta de entrada e o prazer, mais um motivo para voltar.', [b('Razão 1: a cliente já vive assim')]),
 ('16', 'Chocolate', 'O cacau caiu, mas o chocolate na prateleira subiu 24,8% em 12 meses (IPCA).', [b('Razão 2: as portas abertas')]),
 ('19', 'Vila Madalena', 'Caso contextualizado, ao lado de Holambra e Alphaville, com o que vai e o que fica.', [b('Razão 5: a prova na própria rede')]),
 ('21', 'Categorias', 'Árvore de 16 setores da rede; Kids e Peso separados; “Caixa” deixou de ser categoria e é só a zona de conveniência.', [b('As categorias indicadas')]),
 ('22', 'Proteínas', 'Veganas junto das outras proteínas, numa prateleira própria.', [m('ficha de Proteínas', 'gc')]),
 ('26 e 125', 'Produtos fora de categoria', 'Imagens refeitas pela classificação conferida; na versão 4, produtos de higiene saíram dos setores de alimento.', [b('Planograma da loja M')]),
 ('31 e 130', 'Tirinhas Glulac', 'Em Sem Glúten, prateleira de biscoitos e snacks, como os outros itens da marca.', [K]),
 ('32', 'Peso', 'Setor próprio, separado de Kids.', [b('As categorias indicadas')]),
 ('33 e 98', 'Body Protein', 'Em Proteínas, prateleira de whey, como no cadastro da rede (4 - Whey Protein). Se a rede preferir pelo uso, vai para Proteína do colágeno, no mesmo setor.', [K]),
 ('35 e 134', 'Barrinhas', 'Barras proteicas em Barras e snacks, inclusive as da Nutrata; caixa e ponta só como exposição secundária.', [K]),
 ('36, 101 e 136', 'Kombucha e chás', 'Kombucha em Geladeira e bebidas prontas, na base e em todas as páginas.', [K]),
 ('53', 'Granel na entrada', 'Alternativas sem obra para bins na parede, com custo por peça.', [b('A lista de execução de cada loja')]),
 ('68', 'Brigadeiro regional', 'Fit Sweet é regional (Nordeste): fica na parte local dessas lojas.', [b('Núcleo, lista e local')]),
 ('70', 'Classificação do granel', 'Núcleo pela curva ABC e pela presença nas lojas; lista aprovada maior.', [b('O que entra em cada parte')]),
 ('73', 'Frutas e vinhos', 'Fruta seca não fica mais ao lado do vinho.', [b('Plano Celebrar')]),
 ('79', 'Nestlé Q10', 'Saiu da recomendação.', [m('marcas', 'marcas')]),
 ('84', 'Azeites', 'Só azeite, pelo preço praticado: de R$ 68 a R$ 108.', [b('A régua de preço por categoria')]),
 ('88', 'Vivea', 'Nos olhos, com pelo menos 2 frentes.', [b('As regras da prateleira')]),
 ('118 e 138', 'Geleias e vinagres', 'Geleia acima do vinagre, em todos os planogramas.', [b('As regras da prateleira')]),
 ('131', 'Produto proteico', 'Conferido na classificação item a item.', [K]),
 ('132', 'Whey Nutrata', 'Whey W100 em Proteínas; barras com whey em Barras e snacks.', [K]),
 ('135', 'Alva', 'Na versão 4, todos os itens da Alva foram para Higiene e cosméticos, fora dos setores de alimento.', [K]),
 ('146', 'Dia do Consumidor e Páscoa', 'Campanha própria do Dia do Consumidor; Páscoa com kit receita de farinha, cacau e castanhas do granel; Dia da Mulher sem alegação.', [b('As campanhas da rede'), b('Calendário mês a mês')]),
 ('147', 'Datas comemorativas', 'Cada data tem nível: campanha, apoio, conteúdo ou em aberto.', [b('Calendário de trade 2027')]),
 ('148', 'Corpus Christi e aniversário', 'Corpus Christi saiu; os 16 anos viraram campanha.', [b('As campanhas da rede')]),
 ('152', 'Dia e Semana do Cliente', 'Campanha com mecânica, vitrine, PDV e exposição.', [b('As campanhas da rede')]),
 ('153', 'Outubro', 'O foco do mês passou a ser o Dia das Crianças, com Outubro Rosa como conteúdo.', [b('Calendário mês a mês')]),
 ('154', 'Black Friday', 'Campanha com esquenta, cronograma, exposição, vitrine e PDV.', [b('As campanhas da rede')]),
]

def lk(ondes):
    out = []
    for t, h in ondes:
        out.append(f'<a href="{h}">{html.escape(t)}</a>' if h else f'<span class="pl">{html.escape(t)}</span>')
    return ' · '.join(out)
def selo(v): return '<span class="st s4">Completado na versão 4</span>' if v == 4 else '<span class="st s2">Feito na versão 2</span>'

n2 = sum(1 for _, _, it in ITENS for x in it if x[5] == 2); n4 = sum(1 for _, _, it in ITENS for x in it if x[5] == 4)
nr = sum(1 for _, _, it in ITENS for x in it if x[7])
corpo = ''
for num, nome, it in ITENS:
    corpo += f'<h2><span>{num}</span> {nome}</h2>'
    for n, pr, tema, pedido, feito, v, onde, dep in it:
        corpo += (f'<article class="it"><header><b>{n}</b><h3>{tema}</h3><span class="pr p{pr[0]}">{pr}</span>{selo(v)}</header>'
                  f'<p class="ped"><i>A rede pediu</i><span>{pedido}</span></p><p><i>O que fizemos</i><span>{feito}</span></p>'
                  f'<p class="on"><i>Onde ver</i><span>{lk(onde)}</span></p>' + (f'<p class="dep"><i>Depende da Divina Terra</i><span>{dep}</span></p>' if dep else '') + '</article>')
pag = ''.join(f'<tr><td><b>{p}</b></td><td>{t}</td><td>{f}<br><small>{lk(o)}</small></td></tr>' for p, t, f, o in PAGS)
deps = ''.join(f'<li><b>{n} {tema}:</b> {dep}</li>' for _, _, it in ITENS for n, pr, tema, ped, f, v, o, dep in it if dep)

doc = f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="robots" content="noindex">
<title>Resposta à devolutiva · Divina Navegação</title><link rel="icon" href="assets/logos/dt-icone-terra.svg">
<link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:ital,opsz,wght@0,8..60,300;0,8..60,400;1,8..60,400&display=swap" rel="stylesheet">
<style>@font-face{{font-family:'General Sans';src:url('assets/fontes/GeneralSans-Variable.ttf');font-weight:200 700}}
:root{{--i:#F7F5F1;--a:#E5DDD1;--c:#7C381F;--t:#461D17;--g:#6F5F55;--o:#596D49;--m:#A9C094;--ac:#CA942A}}
body{{margin:0;background:var(--i);color:var(--t);font:17px/1.5 'General Sans',system-ui,sans-serif}}main{{max-width:980px;margin:0 auto;padding:40px 22px 80px}}
h1,h2,h3{{font-family:'Source Serif 4',Georgia,serif;font-weight:400;line-height:1.12;margin:0}}h1{{font-size:50px;margin:26px 0 10px}}h1 em{{color:var(--c)}}
h2{{font-size:32px;margin:54px 0 14px;display:flex;gap:14px;align-items:baseline}}h2 span{{font-family:'General Sans';font-size:14px;font-weight:600;color:var(--ac);letter-spacing:.08em}}
.m img{{height:26px}}.m{{display:flex;gap:12px;align-items:center}}.m img.l{{height:17px}}.l1{{font-size:20px;color:var(--g);max-width:760px}}
.res{{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin:28px 0}}.res div{{background:var(--a);border-radius:14px;padding:16px 18px}}.res b{{display:block;font-family:'Source Serif 4';font-weight:300;font-size:44px;line-height:1}}.res div:nth-child(2){{background:var(--t);color:var(--i)}}.res div:nth-child(2) b{{color:var(--ac)}}
.it{{background:#fff;border-radius:14px;padding:16px 20px;margin:10px 0;border:1px solid var(--a)}}.it header{{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin-bottom:8px}}.it header b{{font-size:14px;color:var(--c);min-width:30px}}.it h3{{font-size:23px;flex:1}}
.it p{{margin:6px 0;display:grid;grid-template-columns:170px 1fr;gap:12px}}.it p i{{font-style:normal;font-size:12px;font-weight:600;letter-spacing:.06em;text-transform:uppercase;color:var(--g);padding-top:3px}}
.it .ped{{color:var(--g)}}.it .dep{{background:#FBF1DE;border-radius:8px;padding:6px 8px;margin-top:8px}}.it .dep i{{color:var(--c)}}
.pr,.st{{font-size:12px;font-weight:600;border-radius:99px;padding:2px 9px}}.pC{{background:var(--c);color:#fff}}.pA{{background:var(--a)}}.pM{{background:var(--i);border:1px solid var(--a)}}
.s2{{background:var(--m);color:var(--t)}}.s4{{background:var(--ac);color:var(--t)}}a{{color:var(--c)}}.pl{{color:var(--g)}}
table{{border-collapse:collapse;width:100%;font-size:15.5px;margin:12px 0;background:#fff;border-radius:14px;overflow:hidden}}td,th{{padding:9px 12px;border-top:1px solid var(--a);text-align:left;vertical-align:top}}th{{font-weight:600;background:var(--a)}}small{{color:var(--g)}}
.dl{{background:var(--t);color:var(--i);border-radius:14px;padding:18px 22px;margin-top:20px}}.dl h3{{color:var(--ac);font-size:26px;margin-bottom:8px}}.dl li{{margin:6px 0}}.dl a{{color:var(--ac)}}
.f{{font-size:14px;color:var(--g);margin-top:30px}}
@media(max-width:700px){{h1{{font-size:36px}}.res{{grid-template-columns:1fr}}.it p{{grid-template-columns:1fr;gap:2px}}table{{font-size:14px}}}}</style></head><body><main>
<div class="m"><img src="assets/logos/dt-horizontal-terra.svg" alt="Divina Terra"><span>×</span><img class="l" src="assets/logos/75lab-logo-preto.svg" alt="75 LAB"></div>
<h1>Resposta à devolutiva, <em>ponto a ponto</em></h1>
<p class="l1">Devolutiva da Divina Terra sobre o book 2027 (documento de 13/11/2026, recebido em 16/11/2026). Cada ponto diz o que foi feito, em que versão, onde ver e o que ainda depende da rede. Versão atual: 4, de 23/11/2026.</p>
<div class="res"><div><b>{n2}</b>pontos resolvidos na versão 2, em 16/11</div><div><b>{n4}</b>pontos completados na versão 4, em 23/11</div><div><b>{nr}</b>pontos com decisão ou dado da Divina Terra</div></div>
<div class="dl"><h3>O que depende da Divina Terra</h3><ul>{deps}</ul><p style="margin:10px 0 0">Também: validar as áreas propostas (Barras e snacks, Geladeira e bebidas prontas, Cafés funcionais dentro de Performance) e enviar a metragem de São José dos Campos e a venda das 8 lojas que faltam.</p></div>
{corpo}
<h2><span>07</span> Página a página</h2><p class="l1" style="font-size:16px">Páginas do book da versão 1, como citadas na devolutiva.</p>
<table><tr><th>Página</th><th>Tema</th><th>O que fizemos</th></tr>{pag}</table>
<p class="f">Planilhas com venda por loja ou por produto não ficam nesta página: foram enviadas à parte. Histórico de cada entrega em <a href="versoes/">Versões anteriores</a>.</p>
</main></body></html>'''
(R / 'devolutiva.html').write_text(doc)
bad = [x for x in ('—', '–') if x in doc]
print('devolutiva.html', n2 + n4, 'pontos,', len(PAGS), 'páginas,', 'TRAVESSAO!' if bad else 'sem travessao')
