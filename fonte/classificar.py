# Classificação v2: cada SKU recebe setor e prateleira pela árvore de 16 setores da rede
# (drive/setores-categorias-dt.html, "Padrão de rede"), com as regras de domicílio de lá.
# Setores marcados como PROPOSTA não existem na árvore da rede: respondem à devolutiva de 16/11
# (barras e snacks, bebidas prontas) e precisam de validação.
# Entrada: analise/skus_cad.pkl (venda por SKU + depto e categoria do cadastro).
# Saída: analise/classificacao.pkl
import re, unicodedata, pathlib, sys
import pandas as pd

R = pathlib.Path(__file__).resolve().parent.parent

def nz(s):
    s = unicodedata.normalize('NFD', str(s or '').upper())
    return re.sub(r'\s+', ' ', ''.join(c for c in s if unicodedata.category(c) != 'Mn')).strip()

SETORES = ['Proteínas', 'Colágeno & Beleza', 'Vitaminas de A a Z', 'Ômegas', 'Creatina', 'Performance', 'Chás',
           'Equilíbrio & Bem-Estar', 'Saúde Intestinal', 'Imunidade', 'Peso & Composição Corporal',
           'Longevidade Saudável', 'Kids', 'Sem Glúten', 'Granel', 'Gourmet']
PROPOSTA = {'Barras e snacks', 'Geladeira e bebidas prontas'}
FORA = {'Cuidados pessoais e casa', 'Cafeteria da loja', 'Fora do planograma', 'A classificar'}

CAPS = r'CAPS|CAPSULA|COMPRIMIDO|SUPLEMENTO|\b[1-6]\d ?ML\b|\d ?(CPS|CP|CPAS|COMP|TABS?|CAP|GOMAS|SOFTGELS?)\b|\bCPS\b|\bCP\b|SOFTGEL|\bTABS?\b|GOTAS|\bML\b.*(EXTRATO|TINTURA)'
SG_DEP = {'SEM GLUTEN', 'SEM GLUTEN E SEM LACTOSE', 'SEM GLUTEN E SEM ACUCAR'}
SUPL_DEP = {'SUPLEMENTO', 'VITAMINAS', 'FITOTERAPICOS'}

# (setor, prateleira, padrão na descrição, condição extra, justificativa)
# A primeira regra que casa vence. cond recebe o dicionário do SKU.
REGRAS = []
def r(setor, prat, pad, just, cond=None):
    REGRAS.append((setor, prat, re.compile(pad), cond, just))

sup = lambda x: x['dep'] in SUPL_DEP or re.search(CAPS, x['d'])
nao_sup = lambda x: not sup(x)
caps = lambda x: bool(re.search(CAPS, x['d']))

# 1. Fora da gôndola
r('Performance', 'Acessórios', r'CANECA|MIXER|MISTURADOR|BATEDOR', 'Caneca, mixer e acessórios de preparo: junto das coqueteleiras (padrão da rede)')
r('Fora do planograma', 'Materiais e embalagens', r'\bSACOLA|\bSACO (PAPEL|KRAFT)|ETIQUETA|BOBINA|\bCOPO\b|TAMPA (COPO|PARA)|CANUDO|GUARDANAPO|PALHETA|EMBALAGEM PRESENTE', 'Material de loja ou de consumo da cafeteria, não é produto de gôndola')
r('Cuidados pessoais e casa', 'Higiene e cosméticos', r'DESODORANTE|RASPADOR DE LINGUA|SABONETE|SHAMPOO|CONDICIONADOR|CREME DENTAL|PASTA DE DENTE|ESCOVA DENT|ENXAGUANTE|HIDRATANTE (CORP|FACIAL)|PROTETOR SOLAR|REPELENTE|BATOM|\bSERUM\b|DEMAQUIL|ABSORVENTE|COLETOR MENSTR|LENCO UMED|ESPONJA|DETERGENTE|SABAO|AMACIANTE|\bVELA\b|INCENSO|BUCHA VEGETAL|LAVA ROUPA|MULTIUSO|LIP BALM|BALM (HIDRAT|NATURAL|MULTI)|\bFPS\b|OLEO CORPORAL|CREME CORPORAL|CREME (DE )?PENTEAR|ANTIFRIZZ|MODELADOR|\bPENTE\b|ESMALTE|HIDRATANTE (MAOS|LABIAL|FACIL)|EYE PATCH|FIO DENTAL|\bALVA\b', 'Higiene, cosmético ou casa: não está em nenhum dos 16 setores da rede (a Alva é marca de higiene e cosmético: devolutiva, p. 135)')
r('Cuidados pessoais e casa', 'Casa e acessórios', r'AROMATIZ|\bMEIA\b|MEIAS', 'Casa e acessórios: não está em nenhum dos 16 setores da rede', None)

# 2. Linha infantil mora só em Kids (regra de domicílio da rede)
KIDS = r'\bKIDS?\b|INFANTIL|\bBABY\b(?! ?(BEEF|LEAF|BRIE|CENOURA|ESPINAFRE|MILHO|TOMATE|BATATA|ROMANA|CORN))(?<!PIZZA BABY)|VITAMINI|CHOCOLITO|CRIANCA|\bJUNIOR\b|\bJR\b|PAPAPA|NUTRIKIDS|\bTEEN|BABYSOFT|\bBEBE\b'
r('Kids', 'Suplementos', KIDS, 'Linha infantil mora só em Kids, qualquer que seja a categoria (regra de domicílio da rede)', sup)
r('Kids', 'Café da manhã', r'(' + KIDS + r').*(CEREAL|GRANOLA|ACHOCOLAT|BEBIDA|\bMEL\b|GELEIA|PANQUECA|MINGAU|LEITE)|(CEREAL|GRANOLA|ACHOCOLAT|BEBIDA|\bMEL\b|GELEIA|PANQUECA|MINGAU).*(' + KIDS + r')', 'Linha infantil de café da manhã mora em Kids (regra de domicílio da rede)')
r('Kids', 'Lanches e lancheira', KIDS, 'Linha infantil mora só em Kids, qualquer que seja a categoria (regra de domicílio da rede)')

# 3. Granel: tudo que é vendido a granel mora no Granel
gran = lambda x: x['dep'] == 'A GRANEL' or re.search(r'A GRANEL|\bGRANEL\b', x['d'])
r('Geladeira e bebidas prontas', 'Kombucha', r'KOMBUCHA', 'Kombucha é bebida pronta e fermentada, não é chá; precisa de refrigeração (devolutiva 2.5)')
r('Cafeteria da loja', 'Cafeteria', r'^DT CAFE|\bDT CAFE\b', 'Prato da cafeteria cadastrado no departamento A GRANEL: não é produto de bin', gran)
r('Granel', 'Chás e snacks', r'\bCHA\b|CHAS\b|INFUS|HIBISCO|CAMOMILA|ERVA|FOLHA|DRAGE|CHOCOLATE|CONFEIT|\bBALA|JUJUBA|GOMA|GOMINHA|PACOCA|TRUFA|BISCOIT|COOKIE|ROSQUINHA|SNACK|CHIPS|PALITO|SALGADINHO|CROCANTE|GRANULADO|CAFE|CAPPUC|JAPONES|WASABI|CROC|BANANA PASSA CHOC|COBERT', 'Chás, doces e snacks a granel (bloco de bins da rede)', lambda x: gran(x) and not re.search(r'MIX DE CASTANHA|FARINHA|GRANOLA', x['d']))
r('Granel', 'Grãos, cereais e farinhas', r'FARINHA|GRANOLA|AVEIA|FLOCO|FARELO|CEREAL|MUESLI|ACUCAR|ERITRITOL|XILITOL|ADOCANTE|\bARROZ|FEIJAO|LENTILHA|GRAO DE BICO|ERVILHA|MILHO|PIPOCA|TRIGO|CUSCUZ|QUINOA|AMIDO|POLVILHO|FECULA|TAPIOCA|TEXTURIZADA|\bSOJA|CACAU EM PO|\bPTS\b|SEMOLA|CEVADA|CENTEIO|TRIGUILHO|SAGU', 'Grãos, cereais, farinhas e granolas a granel (bloco de bins da rede)', gran)
r('Granel', 'Sementes e temperos', r'SEMENTE|\bCHIA\b|LINHACA|GERGELIM|GIRASSOL|ABOBORA|AMARANTO|TEMPERO|PIMENTA|OREGANO|CURRY|CURCUMA|PAPRICA|CANELA|CRAVO|COMINHO|NOZ MOSCADA|ACAFRAO|\bSAL\b|ERVAS|LOURO|ALECRIM|MANJERIC|GENGIBRE|ALHO|CEBOLA|COLORAU|CHIMICHURRI|LEMON PEPPER|LEVEDURA|FERMENTO|MOSTARDA EM GRAO|ZAATAR|SALSA|CEBOLINHA|TOMILHO|ERVA DOCE', 'Sementes e temperos a granel (bloco de bins da rede)', gran)
r('Granel', 'Castanhas e frutas secas', r'CASTANHA|\bNOZ|NOZES|AMENDOA|AMENDOIM|PISTACHE|MACADAMIA|AVELA|PECAN|DAMASCO|TAMARA|\bUVA\b|PASSA|AMEIXA|CRANBERRY|BANANA|ABACAXI|MANGA|GOJI|FIGO|MIRTILO|BLUEBERRY|COCO|MACA DESID|DESIDRAT|CRISTALIZ|FRUTA|\bMIX\b|PASTA DE|BARU|CAJU|PEQUI', 'Castanhas, nozes e frutas secas a granel (bloco de bins da rede)', gran)
r('Granel', 'Grãos, cereais e farinhas', r'.', 'Grãos, cereais, farinhas e granolas a granel (bloco de bins da rede)', gran)

# 3b. Produtos reconhecidos pelo nome comercial (o nome não diz o ativo)
NOMES = [
    (r'ARTRO|CARTLIV|CARTIL|CURCU.*(TIPO II|TIPO 2)|(TIPO II|TIPO 2).*CURCU', 'Colágeno & Beleza', 'Articular'),
    (r'\bMG COMPLEX|TRIMAG|\bMAG ?\d+|BIOMAG|\bMAG\b.*CAPS|MAGNES|TREONATO', 'Equilíbrio & Bem-Estar', 'Calma & equilíbrio'),
    (r'INUSITOL|ASW?AGANDHA|ASHWA', 'Equilíbrio & Bem-Estar', 'Calma & equilíbrio'),
    (r'GUARANA', 'Equilíbrio & Bem-Estar', 'Foco & memória'),
    (r'\bALPHA \d+ ?CAPS|\bCALC\b', 'Vitaminas de A a Z', 'Multivitamínicos'),
    (r'SIM ?CAPS', 'Saúde Intestinal', 'Probióticos'),
    (r'\bGUT\b', 'Saúde Intestinal', 'Complementares'),
    (r'LACZYM|ZYME', 'Saúde Intestinal', 'Enzimas'),
    (r'GOLDENLIFT|GOLDEN MILK', 'Saúde Intestinal', 'Complementares'),
    (r'PRE ACTION|ARGIN|TAURIN', 'Performance', 'Antes do treino'),
    (r'H2GEL|\bHIDRA\b|HYDRATE|ELECTROLYT|ENERGY ?KICK', 'Performance', 'Durante o treino'),
    (r'CREA ?POWER', 'Creatina', 'Creatina em pó'),
    (r'VEGAN ?PRO\b|\bPROT VEG|EAT CLEAN PROT', 'Proteínas', 'Veganas'),
    (r'ISO PROT|100 ?WHEY|\bWHEY', 'Proteínas', 'Whey'),
    (r'FEEL COMPLETE', 'Peso & Composição Corporal', 'Substitutos de refeição'),
    (r'APETIT|BERBERIN|MORES ?BELT|\bMORO\b|APPLE CIDER|\bFIRE\b|GLUCOMAN', 'Peso & Composição Corporal', 'Metabolismo'),
    (r'BLACK MACA|MACA (POWDER|PERUANA|EM PO|PREMIUM)|FENO GREGO.*(CAPS|\d ?MG)|DHEA', 'Longevidade Saudável', 'Saúde do homem'),
    (r'AMORA|GUMMY.*AMORA', 'Longevidade Saudável', 'Saúde da mulher'),
    (r'\bNAC\b', 'Longevidade Saudável', 'Antioxidantes'),
    (r'GEL REAL|GELEIA REAL', 'Imunidade', 'Naturais da colmeia'),
    (r'GREEN SHOT', 'Imunidade', 'Fitoterápicos'),
    (r'\bCOLAG\b', 'Colágeno & Beleza', 'Beleza'),
    (r'GAMALIFT|GOOD MOOD|\bMOOD\b', 'Equilíbrio & Bem-Estar', 'Calma & equilíbrio'),
    (r'MELATONIN|SLEEFOR', 'Equilíbrio & Bem-Estar', 'Sono de qualidade'),
    (r'VITALIFT|V-?FORT\b|GUARDIAN|GUARDIN', 'Vitaminas de A a Z', 'Multivitamínicos'),
    (r'\bFE COMPLEX', 'Vitaminas de A a Z', 'Minerais'),
    (r'COMPLEX ?B\b|B ?COMPLEX', 'Vitaminas de A a Z', 'Vitaminas isoladas'),
    (r'VITAMINI|VITAMIN\b', 'Vitaminas de A a Z', 'Vitaminas isoladas'),
    (r'SIMFORT|PURABIOTIC|\bPROBIO\b|BIOTIC', 'Saúde Intestinal', 'Probióticos'),
    (r'ENZY|GUT BALANCE', 'Saúde Intestinal', 'Enzimas'),
    (r'GLUTAMIN', 'Saúde Intestinal', 'Complementares'),
    (r'^(?!.*(TIPO II|TIPO 2|ARTIC|CARTIL)).*CURCU', 'Saúde Intestinal', 'Complementares'),
    (r'BETA ACTION|DOBRO.*\bBT\b|\bBT ?400|HEAT UP', 'Performance', 'Antes do treino'),
    (r'MUSCLE SYNERGY|AMINNU', 'Performance', 'Depois do treino'),
    (r'HYDROLIFT|HIDROGEL|\b\d+ ?CARBS?\b|\bCARBS\b|PALATINOSE', 'Performance', 'Durante o treino'),
    (r'(CREATIN|CREALIVE|CREAPURE|CREALIFT|CREAFORT).*(GOMA|GUMM|CAPS|CUBO|SACHE|\b[1-9] ?G\b|STICK|MONODOSE)|(GOMA|GUMM|CUBO).*(CREATIN|CREAPURE)', 'Creatina', 'Formatos práticos'),
    (r'CREATIN|CREALIVE|CREAPURE|CREALIFT|CREAFORT', 'Creatina', 'Creatina em pó'),
    (r'ISOFORT|CARNIBOL', 'Proteínas', 'Whey'),
    (r'VEGANDELIGHT', 'Proteínas', 'Veganas'),
    (r'BORAPRIM|ALPHA MATER|\bSHE\b', 'Longevidade Saudável', 'Saúde da mulher'),
    (r'LONG JACK|TONGKAT|TRIBUL', 'Longevidade Saudável', 'Saúde do homem'),
    (r'ACETIL ?CISTEINA|RESTAURE|INFLAMINUS', 'Longevidade Saudável', 'Antioxidantes'),
    (r'HEPAT|TERMOPLUS|DERRETE|CHA ABDOMEN|\bMCT\b|\bTCM\b', 'Peso & Composição Corporal', 'Metabolismo'),

    (r'COLAGEN', 'Colágeno & Beleza', 'Beleza'),
    (r'\bPROP\b|PROPOLIS', 'Imunidade', 'Naturais da colmeia'),
    (r'(?!.*(WHEY|PROTEIN))(IMMUN|\bIMUNE|COLOSFORT|COLOSTRO|SHOT MATINAL|MORNING SHOT)', 'Imunidade', 'Fitoterápicos'),
]
for pad, setor, prat in NOMES:
    r(setor, prat, pad, f'Produto reconhecido pelo nome comercial; ativo principal mora em {setor} (padrão da rede)',
      lambda x: (x['dep'] in SUPL_DEP or x['dep'] in ('DIVERSOS', 'ORGANICOS', 'PRODUTOS NATURAIS', 'VEGANOS', 'IMPORTACAO') and re.search(CAPS + r'|\d ?ML\b|\d{3} ?G\b|SACHE|LATA', x['d'])) and not re.search(r'BARRA|\bBAR\b|WAFER|COOKIE|PACOC', x['d']))

# 4. Bebidas prontas (proposta: tirar das categorias de chá e de suplemento)
r('Geladeira e bebidas prontas', 'Funcionais prontas', r'\b(1[5-9]\d|[2-9]\d\d|1\d{3}) ?ML\b|\b1 ?L\b|\bRTD\b|ALOE VERA.*BEBIDA|BEBIDA.*ALOE', 'Bebida pronta para beber: vai para a geladeira, separada dos suplementos em pó (devolutiva 2.5)', lambda x: not re.search(r'AZEITE|VINAGRE|OLEO|\bMCT\b|\bTCM\b|XAROPE|MOLHO|SHOYU|\bMEL\b|SPRAY|COQUETELEIRA|GARRAFA|SQUEEZE|SHAKER|COPO|EXTRATO|ESSENCIA|AROMA|VINHO|ESPUMANTE|CERVEJA|GIN\b|LICOR|DESODOR|SHAMPOO|SABONETE|CREME|LEITE|BEBIDA VEGETAL|BEBIDA DE (AVEIA|AMENDOA|ARROZ|COCO|CASTANHA|SOJA)|BONE BROTH|CALDO|GELEIA|LIMPA|LIQUID|LIQUIDO|CONCENTRAD|OMEGA|\bDHA\b|GABA|BARISTA|CASTANHA|AMENDOA|AVEIA|\bCOCO\b|ARROZ|SOJA|XAROPE|GOTAS|SPRAY', x['d']) and x['dep'] != 'A GRANEL')
r('Geladeira e bebidas prontas', 'Proteicas prontas', r'(PROTEIN|PROTEINA|WHEY|YOPRO|IOPRO).*(\d+ ?ML\b|PRONTO|DRINK|SHAKE PRONTO|BEBIDA)|BEBIDA (LACTEA )?PROTEICA', 'Bebida proteica pronta para beber: vai para a geladeira, não para a gôndola de proteína em pó')
r('Geladeira e bebidas prontas', 'Energéticos e funcionais', r'ENERGY DRINK|ENERGETICO|\bTNT\b|RED BULL|MONSTER|\bLATA\b.*(ENERG|CAFEINA)|ISOTONICO PRONTO|AGUA DE COCO|\bAGUA\b|SUCO|REFRIGERANTE|SODA|TONICA|CHA GELADO|ICE TEA|LEMONADE|LIMONADA|SPARKLING|FRISANTE', 'Bebida pronta: separada de chás e de suplementos em pó (devolutiva 2.5)', lambda x: not caps(x) and x['cat'] != '24 - ENERGY GEL' and re.search(r'\d ?ML\b|\d ?L\b|\bLATA\b|\bPET\b|GARRAFA', x['d']) and not re.search(r'ELETROLIT|COLLAGEN|COLAGEN|\d ?G\b', x['d']))

r('Geladeira e bebidas prontas', 'Refrigerados', r'\bIOG\b|IOGURTE|KEFIR|QUEI(JO)? VEG|\bTOFU\b|COALHADA|REQUEIJAO VEG|CREME DE QUEIJO VEG', 'Produto refrigerado: fica na geladeira, junto das bebidas prontas (proposta)', lambda x: not caps(x))

# 5. Barras e snacks (proposta, devolutiva 2.6)
r('Barras e snacks', 'Barras proteicas', r'(\bBARRA|\bBAR\b|BARRINHA|WAFER|\bBITES?\b|CRISP|CRUNCH|COOKIE|ALFAJOR|BROWNIE|BOMBOM|PALHA|TORTINHA|CHIPS|TIRINHA|PIPOCA).*(PROTEIN|PROTEINA|PROTEICA|PROTEICO|WHEY|\d+ ?G (DE )?PROT|\bPRO\b)|(PROTEIN|PROTEICA|PROTEICO|WHEY).*(\bBARRA|\bBAR\b|BARRINHA|WAFER|\bBITES?\b|CRISP|COOKIE|ALFAJOR|BROWNIE|BOMBOM|CHIPS|TIRINHA|PIPOCA|SNACK)|BARRA CHARGE|GREG BAR|BOLD\b|\bNUBAR|\bNUTRY PROT|TOP WHEY BAR|PROTEIN CRISP', 'Barra ou snack proteico: categoria própria de barras e snacks (devolutiva 2.6), e não Proteínas', lambda x: not re.search(r'\b([2-9]\d\d|\d{4}) ?G\b|\bKG\b|DOSES|SACHES|\bPOTE|REFIL', x['d']) or re.search(r'CRISP|CHIPS|SNACK|\bBITES', x['d']))
r('Barras e snacks', 'Barras proteicas', r'PACOC.*(WHEY|PROT)|ISOCRISP|\bMONDZ|(PROTEIN|PROTEICA).*(CROC|TORRAD|CRACKER|CHIPS|SNACK)', 'Snack proteico: categoria própria de barras e snacks (devolutiva 2.6)')
r('Barras e snacks', 'Barras proteicas', r'.', 'Cadastro da rede marca como barrinha de proteína', lambda x: x['cat'] == '15 - BARRINHA PROTEÍNA')
r('Barras e snacks', 'Barras de cereais, frutas e castanhas', r'\bBARRA|\bBAR\b|BARRINHA|\bNUTS BAR|\bCEREAL BAR|BARRA DE (CEREAL|FRUTA|CASTANHA|NUTS|AMENDOIM|COCO|CHOCOLATE)', 'Barrinha embalada: categoria própria de barras e snacks (devolutiva 2.6); a rede hoje espalha por vários setores', lambda x: not re.search(r'BARRA DE (CHOCOLATE|CACAU)|CHOCOLATE (AO LEITE|AMARGO|BRANCO|MEIO AMARGO|\d)|\d+ ?% ?(CACAU)?|CACAU|TABLETE|HAOMA|DIVINE|NUGALI|ARTESANA|LINDT|SABONETE|DESODORANTE', x['d']))

# 6. Creatina (todas as marcas e formatos)
r('Creatina', 'Formatos práticos', r'(CREATINA|CREAPURE|CREATINE|\bCREA\b).*(GOMA|GUMMY|GUMMIES|SACHE|CAPS|MONODOSE|STICK|TABLET|BALA)|(GOMA|GUMMY|GUMMIES|SACHE|STICK).*(CREATINA|CREAPURE|CREATINE)', 'Creatina em formato prático; toda creatina mora em Creatina (padrão da rede)')
r('Creatina', 'Creatina em pó', r'CREATINA|CREAPURE|CREATINE|\bCREA\b|CREALIFT|CREAFORT', 'Toda creatina mora em Creatina, de todas as marcas (padrão da rede)')

# 7. Colágeno: proteína do colágeno vai para Proteínas; beleza e articular para Colágeno & Beleza
r('Colágeno & Beleza', 'Articular', r'TIPO II|TIPO 2\b|UC ?II|UC-II|ARTICUL|CONDROITINA|GLUCOSAMINA|\bMSM\b|MOBILIDADE|\bJOINT|CARTILAG|COLAGENO.*(II|ARTIC)', 'Colágeno tipo II e ativos articulares: prateleira Articular (padrão da rede)')
r('Proteínas', 'Proteína do colágeno', r'(PROTEIN|PROTEINA).*COLAGEN|COLAGEN.*(PROTEIN|PROTEINA)|COLLAGEN PROTEIN|BODY BALANCE PROT|PEPTIDEOS? DE COLAGENO.*(\d{3,4} ?G|KG)', 'Proteína do colágeno mora em Proteínas (padrão da rede)')
r('Colágeno & Beleza', 'Beleza', r'COLAGENO|COLLAGEN|VERISOL|PEPTAN|BODYBALANCE', 'Colágeno de beleza mora em Colágeno & Beleza (padrão da rede)')
r('Colágeno & Beleza', 'Ativos e fórmulas', r'BIOTINA|SILICIO|HIALURON|\bHAIR\b|\bSKIN\b|\bNAILS?\b|UNHAS|CABELO|\bBEAUTY|BELEZA|PELE\b|EXIMIA|IMECAP|INNEOV', 'Ativo ou fórmula de beleza mora em Colágeno & Beleza (padrão da rede)', sup)

# 8. Proteínas em pó
r('Proteínas', 'Veganas', r'(PROTEIN|PROTEINA|\bPROT\b).*(VEGAN|VEGETAL|PLANT|ERVILHA|\bPEA\b|ARROZ|SOJA|GRAO DE BICO|ABOBORA)|(VEGAN|VEGETAL|PLANT|ERVILHA|\bPEA\b).*(PROTEIN|PROTEINA|\bPROT\b)|VEGAN PROT|PROTEINA VEG', 'Proteína vegetal: fica no setor Proteínas, ao lado das demais, para o cliente comparar alternativas (padrão da rede e devolutiva 2.3)', lambda x: not re.search(r'GRANOLA|CEREAL|BISCOIT|COOKIE|\bPAO\b|MASSA|SNACK|CHIPS|BARRA|WAFER|PANQUECA|BOLO|CROC|PASTA', x['d']))
r('Proteínas', 'Beef protein', r'\bBEEF\b|CARNE BOVINA|HYDROBEEF|CARNIVOR', 'Beef protein mora em Proteínas (padrão da rede)', lambda x: not re.search(r'JERKY|CHARQUE|SNACK', x['d']))
r('Proteínas', 'Albumina', r'ALBUMINA|CLARA DE OVO|EGG PROTEIN|PROTEINA DO OVO', 'Albumina mora em Proteínas (padrão da rede)')
r('Performance', 'Depois do treino', r'HIPERCALOR|MASS\b|GAINER|HIPER CALOR', 'Hipercalórico é produto de treino; não está na lista de Proteínas da rede', lambda x: x['dep'] == 'SUPLEMENTO')
r('Proteínas', 'Whey', r'\bWHEY|\bW100\b|ISOLAD[AO]|HIDROLISAD[AO]|CONCENTRAD[AO]|\b3W\b|BODY PROTEIN|PROTEIN (BLEND|POWDER|\d+ ?G)|\bPROTEIN\b|PROTEINA (EM PO|ISOLADA|CONCENTRADA)|NUTRI WHEY|ISO ?WHEY', 'Whey e proteínas em pó moram em Proteínas (padrão da rede)', lambda x: x['dep'] in SUPL_DEP or x['dep'] == 'IMPORTACAO' or x['cat'] in ('4 - WHEY PROTEIN', '2 - PROTEINA') or re.search(r'\b([2-9]\d\d|\d{4}) ?G\b|\bKG\b', x['d']) and not re.search(r'BARRA|\bBAR\b|WAFER|COOKIE|BISCOIT|PAO\b|GRANOLA|CEREAL|SNACK|CHIPS|PANQUECA|PASTA', x['d']))

# 9. Ômegas (inclui coenzima Q10 e fitosteróis, pelo padrão da rede)
r('Ômegas', 'Complementares', r'COENZIMA|COQ ?10|\bQ10\b|UBIQUINOL|FITOSTEROL', 'Coenzima Q10 e fitosteróis moram em Ômegas (padrão da rede)')
r('Ômegas', 'Fontes vegetais', r'(OLEO|OMEGA).*(LINHACA|CHIA|ALGA|VEGAN|VEGETAL|PERILLA|SACHA)|OMEGA ?3.*VEG|ALGAE', 'Ômega de fonte vegetal (padrão da rede)', sup)
r('Ômegas', 'Ômega 3 e DHA', r'\bOMEGA|\bDHA\b|\bEPA\b|KRILL|OLEO DE PEIXE|FISH OIL|SUPER OMEGA|OMEGAFOR|MEGA ?DHA|\bTG\b.*(EPA|DHA)', 'Ômega 3, EPA e DHA (padrão da rede)', lambda x: sup(x) or not re.search(r'\bOVO|OVOS|BISCOIT|PAO\b|GRANOLA|BARRA|LEITE|MARGARINA|PASTA|SEMENTE', x['d']))

# 10. Saúde intestinal (inclui glutamina e cúrcuma, pelo padrão da rede); antes de vitaminas por causa de "ENZIMA"
r('Saúde Intestinal', 'Probióticos', r'PROBIOTIC(?!A\b)|PROBIOTICO|SIMBIOT|LACTOBAC|BIFIDO|\bUFC\b|FLORA ?TIL|FLORATIL|SACCHAROMYCES|FEMIBIOTIC|ENTEROGERMINA|BIOFLORA|KEFIR.*(CAPS|PO)', 'Probióticos e simbióticos (padrão da rede)')
r('Saúde Intestinal', 'Prebióticos e fibras', r'PREBIOT|PSYLLIUM|PSYLIUM|INULINA|\bFOS\b|FIBRA|FIBER|BETA ?GLUCANA|GOMA GUAR|SLIM FIBER', 'Prebióticos e fibras (padrão da rede)', lambda x: sup(x) or re.search(r'PSYLL|PSYL|INULINA|FIBRA EM PO|FIBER', x['d']))
r('Saúde Intestinal', 'Enzimas', r'(?<!CO)ENZIMA|\bENZYM|LACTASE|DIGEST|BROMELINA|PAPAINA|PEPTOZIL', 'Enzimas digestivas e lactase (padrão da rede)', sup)
r('Saúde Intestinal', 'Complementares', r'GLUTAMINA|GLUTAMINE|CURCUMA|TURMERIC|CURCUMINA|CARVAO ATIVADO|BOLDO.*CAPS|ESPINHEIRA', 'Glutamina e cúrcuma moram em Saúde Intestinal (padrão da rede)', sup)

# 11. Peso & Composição Corporal (cromo fica aqui, pelo padrão da rede)
r('Peso & Composição Corporal', 'Substitutos de refeição', r'SUBSTITUTO|SHAKE\b|SHAKE (DIET|NUTRI)|NUTRI ?SHAKE|DIETSHAKE|REFEICAO', 'Shake substituto de refeição (padrão da rede)', lambda x: x['dep'] in SUPL_DEP or x['cat'] == '20 - SHAKE' or x['dep'] == 'DIET')
r('Peso & Composição Corporal', 'Saciedade', r'SACIEDADE|GLUCOMANAN|KONJAC|CHITOSAN|QUITOSANA|FAIXA ?BRANCA|FASEOLAMINA|FEIJAO BRANCO', 'Saciedade (padrão da rede)', sup)
r('Peso & Composição Corporal', 'Metabolismo', r'TERMOGEN|THERMO|\bCROMO|PICOLINATO|\bCLA\b|CARNITINA|CAFE VERDE|CHA VERDE|GENGIBRE|VINAGRE DE MACA|LARANJA MORO|\bMORO\b|FAST METABOLISM|HEPATOFOR|BERBERINA|\bLIPO ?(6|RED|BLACK|BURN)\b|\bSLIM\b|SECA|EMAGREC|DETOX|DRENA|METABOL|GLP|SEMAGLU|OZ.MPIC|CAPSIAICINA|PIMENTA.*CAPS|CHA (DE )?CAVALINHA.*CAPS|BURN', 'Ativos de metabolismo e composição corporal (padrão da rede)', lambda x: sup(x) or x['cat'] == '19 - TERMOGENICO')

# 12. Equilíbrio & Bem-Estar (magnésio fica aqui, pelo padrão da rede)
r('Equilíbrio & Bem-Estar', 'Sono de qualidade', r'MELATONINA|TRIPTOFANO|GLICINA|\bSLEEP|\bSONO\b|DORMIR|\bNIGHT\b|\bNOITE\b|KOALA|VALERIANA|OLEO ESSENC|DIFUSOR|ROLL ?ON.*(LAVANDA|SONO)', 'Sono de qualidade (padrão da rede)')
r('Equilíbrio & Bem-Estar', 'Calma & equilíbrio', r'MAGNESIO|MAGNESIUM|TEANINA|THEANINE|\bGABA\b|ASHWAG|RHODIOLA|ADAPTOG|INOSITOL|PASSIFLORA|MULUNGU|\bCALM|RELAX|ANSIED|ESTRESSE|STRESS|SAFFRON|ACAFRAO.*CAPS|\b5.?HTP|SERENA|EQUILIBR', 'Calma e equilíbrio; magnésio em todas as formas mora aqui (padrão da rede)', sup)
r('Equilíbrio & Bem-Estar', 'Foco & memória', r'NOOTROP|\bBRAIN|\bFOCO\b|FOCUS|MEMORIA|COGNI|LION.?S MANE|JUBA DE LEAO|GINKGO|BACOPA|FOSFATIDIL|CITICOLINA|\bMENTE\b|\bMIND\b|ENERGIA MENTAL|GUARANA.*CAPS|GINSENG', 'Foco e memória, inclusive fórmulas com cafeína (padrão da rede)', sup)

# 13. Longevidade Saudável
r('Longevidade Saudável', 'Saúde da mulher', r'PRIMULA|BORRAGEM|CRANBERRY|CLIMATER|MENOPAUS|\bTPM\b|CICLO|FEMININ|MULHER|WOMAN|WOMEN|\bFEM\b|AMORA ?BRANCA|ISOFLAVONA|INOSITOL.*MULHER|GESTA|PRE ?NATAL|FERTIL', 'Saúde da mulher (padrão da rede)', sup)
r('Longevidade Saudável', 'Saúde do homem', r'PROSTATA|SAW PALMETTO|HOMEM|\bMEN\b|\bMAN\b|MASCULIN|TRIBULUS|MACA PERUANA|BLACK MACA|MACA (EM )?PO\b|MACA (NEGRA|AMARELA|ROXA|GELATINIZADA)|TESTO|LIBIDO|VIGOR', 'Saúde do homem (padrão da rede)', sup)
r('Longevidade Saudável', 'Antioxidantes', r'RESVERATROL|ANTIOX|ASTAXANT|\bNAC\b|ACETILCISTEINA|\bPQQ\b|LUTEINA|ZEAXANT|LICOPENO|QUERCETINA|\bNMN\b|NAD\+?|ESPERMIDINA|LONGEV|GLUTATIONA|SPIRULIN|ESPIRULIN|CLORELA|CHLORELLA|ALGA', 'Antioxidantes e longevidade (padrão da rede)', sup)

# 14. Imunidade (colmeia e fitoterápicos sazonais); a linha de vitamina C, D e zinco fica em Vitaminas
r('Imunidade', 'Naturais da colmeia', r'PROPOLIS|GELEIA REAL|\bMEL\b|COLMEIA|APITOX|POLEN', 'Própolis, mel e geleia real moram em Imunidade (padrão da rede)', lambda x: not re.search(r'SABOR|PAO DE MEL|\b(C/|COM|E) MEL\b|MOSTARDA|MOLHO|CHIPS|BISCOIT|BARRA|GRANOLA|DOCE DE|BOLO|PROTEIN|WHEY|\bCHA\b|CEREAL|IOGURTE|AMENDOIM|CASTANHA|MEL ?ADO|MELADO', x['d']))
r('Imunidade', 'Fitoterápicos', r'EQUINACEA|ECHINACEA|SABUGUEIRO|UNHA DE GATO|AGUAPEI|OREGANO.*(OLEO|CAPS)|EXTRATO|TINTURA|FITOTER|MORINGA|ALHO.*CAPS|ACEROLA.*CAPS|CAMU|GUACO|XAROPE|CHA.*CAPS|ERVA.*CAPS', 'Fitoterápicos de suporte (padrão da rede)', lambda x: sup(x) and not re.search(r'BAUNILHA|ESSENCIA|AROMA', x['d']))

# 15. Performance
r('Performance', 'Acessórios', r'COQUETELEIRA|SHAKER|\bSQUEEZE|GARRAFA|CAPSULEIRA|PORTA ?(SUPLEMENTO|CAPSULA|PILULA)|\bFUNIL|GALAO|TUMBLER|TERMICA|COPO (TERMICO|INOX)|POTE DOSADOR', 'Coqueteleiras, garrafas e porta-suplemento (padrão da rede)')
r('Performance', 'Durante o treino', r'\bGEL\b|ENERGY GEL|CARB UP|PALATINOSE|RIBOSE|MALTODEXTRIN|DEXTROSE|WAXY|ISOTONIC|ELETROLIT|HIDRATA|SAL DE CORRIDA|\bSALT\b|ENDURANCE|\bCARBO', 'Géis, carboidratos e eletrólitos de treino (padrão da rede)', lambda x: x['dep'] in SUPL_DEP or x['cat'] == '24 - ENERGY GEL')
r('Performance', 'Antes do treino', r'PRE.?TREINO|PRE.?WORKOUT|PRETREINO|CAFEINA|CAFFEINE|BETA ?ALANINA|CITRULINA|ARGININA|TAURINA|NITRATO|BETERRABA.*(PO|CAPS)|\bNO2\b|PUMP|\bHORUS|OVERDOSE|EVORA|\bINSANE', 'Pré-treino e cafeína isolada (padrão da rede)', lambda x: x['dep'] in SUPL_DEP or x['cat'] == '9 - PRÉ TREINO')
r('Performance', 'Depois do treino', r'BCAA|\bEAA\b|AMINO|LEUCINA|\bHMB\b|ZMA\b|RECOVERY|RECUPERA', 'BCAA e aminoácidos (padrão da rede)', lambda x: x['dep'] in SUPL_DEP or x['cat'] == '11 - AMINOÁCIDO')

# 16. Vitaminas de A a Z (linha completa de C, D e zinco fica aqui)
r('Vitaminas de A a Z', 'Multivitamínicos', r'MULTIVIT|POLIVIT|\bA-Z\b|\bA A Z\b|\bAZ\b|CENTRUM|\bMULTI\b|DAILY|COMPLETO', 'Multivitamínicos (padrão da rede)', sup)
r('Vitaminas de A a Z', 'Minerais', r'\bZINCO|\bZINC\b|FERRO\b|FERRITIN|\bIRON\b|CALCIO|CALCIUM|SELENIO|IODO|POTASSIO|BORO|\bCOBRE\b|MANGANES|SILICIO|LITIO|QUELATO|BISGLICINATO', 'Minerais de base (padrão da rede)', sup)
r('Vitaminas de A a Z', 'Vitaminas isoladas', r'VITAMINA|\bVIT\b|\bVIT ?[ABCDEK]\d*\b|\bD3\b|\bD3 ?K2|\bK2\b|\bB12\b|METILCOBALAMINA|COMPLEXO B|\bB COMPLEX|METILFOLATO|ACIDO FOLICO|FOLATO|NIACINA|BIOTINA|\bC ?1000|ACIDO ASCORBICO|ASCORBATO|LIPOSSOMAL', 'Vitaminas isoladas (padrão da rede)', sup)
r('Vitaminas de A a Z', 'Vitaminas isoladas', r'.', 'Cadastro da rede marca como vitamina ou mineral', lambda x: x['cat'] in ('14 - VITAMINAS E MINERAIS', '7 - VITAMINAS'))

# 17. Chás em caixa, sachê e lata (chá a granel já caiu no Granel)
cha = lambda x: not caps(x) and (x['dep'] in ('CHAS', 'CHAS E TEMPEROS') or x['dep'] in ('ORGANICOS', 'PRODUTOS NATURAIS', 'GOURMET', 'IMPORTACAO', 'DIVERSOS', 'DIET', 'VEGANOS', 'SEM LACTOSE') and re.search(r'\bCHA\b|CHAS\b|INFUS|\bTEA\b|TISANA|SACHES', x['d'])) and not re.search(r'\d ?ML\b|CHOCO|BISCOIT|BARRA', x['d'])
r('Chás', 'Presenteáveis', r'\bLATA\b|\bKIT\b|PRESENTE|COFFRET|SORTID|COLECAO|CAIXA DE MADEIRA', 'Chá em lata ou kit presenteável (padrão da rede)', lambda x: cha(x) and re.search(r'\bCHA\b|CHAS\b|INFUS|TEA\b|TISANA', x['d']) or x['cat'] == '5 - LATA' and x['dep'] in ('CHAS', 'CHAS E TEMPEROS'))
r('Chás', 'Relaxar', r'CAMOMILA|MELISSA|CIDREIRA|LAVANDA|MARACUJA|PASSIFLORA|MULUNGU|\bCALM|RELAX|\bNOITE|\bNIGHT|SLEEP|DORMIR|TILIA|VALERIANA|ERVA ?DOCE.*CAMOMILA', 'Chá para relaxar (padrão da rede)', cha)
r('Chás', 'Digestivo', r'DESINCHA|BOLDO|HORTELA|ERVA ?DOCE|FUNCHO|CARQUEJA|ESPINHEIRA|ALCACHOFRA|DIGEST|DETOX|DRENA|CAVALINHA|DENTE DE LEAO|SENE|CHA VERDE.*LIMAO|GENGIBRE', 'Chá digestivo (padrão da rede)', cha)
r('Chás', 'Energia e sabor', r'\bCHA\b|CHAS\b|INFUS|TISANA|\bTEA\b|MATE\b|MATCHA|HIBISCO|ROOIBOS|\bCHAI\b|CHIMARRAO|TERERE|GUAYUSA|YERBA', 'Chá em caixa, sachê ou folha embalada (padrão da rede: chá se define pelo formato)', cha)
r('Chás', 'Energia e sabor', r'.', 'Departamento de chás do cadastro, sem marca de tempero', lambda x: x['dep'] == 'CHAS' and not caps(x))

# 18. Sem Glúten (setor de restrição: compõe a alimentação inteira)
sg = lambda x: x['dep'] in SG_DEP or re.search(r'\bSCHAR\b|SEM GLUTEN|S/ ?GLUTEN|GLUTEN FREE|\bSG\b', x['d'])
r('Sem Glúten', 'Farinhas e misturas', r'FARINHA|\bMIX\b|MISTURA|POLVILHO|FECULA|AMIDO|AVEIA|TAPIOCA|FUBA|PREPARO|FERMENTO|MASSA PRONTA PARA', 'Farinhas, mixes e polvilhos sem glúten (padrão da rede)', sg)
r('Sem Glúten', 'Pães, massas e prontos', r'\bPAO|\bPAES|WRAP|PIZZA|PANQUECA|MACARRAO|\bMASSA|ESPAGUETE|PENNE|FUSILLI|LASANHA|NHOQUE|TALHARIM|CONGELAD|PAO DE QUEIJO|TORTA|QUICHE|SALGADO|ESFIRRA|EMPANAD|HAMBURG|LANCHE|MARMITA|SOPA|CALDO|RISOTO|CUSCUZ|BOLO\b|MUFFIN|TORRADA', 'Pães, massas e prontos sem glúten (padrão da rede)', sg)
r('Sem Glúten', 'Complementares', r'GELEIA|MANTEIGA|MOLHO|CERVEJA|CREME|PASTA|DOCE DE|REQUEIJ|QUEIJO|LEITE|BEBIDA|IOGURTE|SORVETE|PATE|AZEITE|OLEO|VINAGRE|TEMPERO', 'Complementares sem glúten (padrão da rede)', sg)
r('Sem Glúten', 'Biscoitos e snacks', r'.', 'Biscoitos e snacks sem glúten; produto do departamento sem glúten fica no setor de restrição (padrão da rede)', sg)

# 19. Gourmet (despensa e ocasião)
r('Gourmet', 'Cafés, vinhos e presenteáveis', r'\bVINHO|ESPUMANTE|PROSECCO|CHAMPAGNE|CAVA\b|CHARDONNAY|MERLOT|CABERNET|MALBEC|SAUVIGNON|MOSCATEL|PINOT|TANNAT|CARMENERE|\bGIN\b|CERVEJA|LICOR|CACHACA|\bSAKE\b|CESTA|\bKIT\b|PRESENTE|PANETONE|COLOMBA|\bCAFE|CAFES\b|COFFEE|CAPSULA.*(NESPRESSO|DOLCE)|CAPPUCCINO|SUPERCOFFEE|\bMOCHA|LATTE', 'Cafés especiais e funcionais, vinhos e presenteáveis (padrão da rede)')
r('Gourmet', 'Doces e chocolates', r'OVO (DE )?PASCOA|DULCE|SUSPIRO|BENDU|CASADINHO|PASTA (DE )?AMEN|BANANINHA|BANANA ZERO|PANTASTICA|LEITINHO|CHOCOLATE|\bCACAU\b|BOMBOM|\bTRUFA|ALFAJOR|BROWNIE|DOCE DE|DOCINHO|BRIGADEIRO|BEIJINHO|PACOCA|GELEIA|COMPOTA|CREME DE (AVELA|PISTACHE|CASTANHA|AMENDOIM|COCO)|PASTA DE (AMENDOIM|CASTANHA|AMENDOA|AVELA|PISTACHE)|MANTEIGA DE (AMENDOIM|CASTANHA|AMENDOA)|NUTELLA|DRAGE|BALA\b|BALAS\b|JUJUBA|GOMA\b|GOMINHA|MARSHMALLOW|NOUGAT|TORRONE|MACARON|COCADA|PE DE MOLEQUE|LINDT|MILKA|RITTER|GAROTO|BISCOFF|DOCE\b|SORVETE|PICOLE|MOUSSE|PUDIM', 'Chocolates, doces de pote, geleias e pastas (padrão da rede)')
r('Gourmet', 'Azeites, molhos e antepastos', r'CARDAMOMO|FENO GREGO|PASTA DE GERG|PARME|AZEITE|VINAGRE|ACETO|BALSAMIC|\bMOLHO|PESTO|\bSUGO|KETCHUP|MOSTARDA|MAIONESE|BARBECUE|TAHIN|SHOYU|TAMARI|\bMISSO|\bMISO\b|WASABI|TEMPERO|\bSAL\b|PIMENTA|CURRY|CURCUMA|PAPRICA|OREGANO|ZAATAR|SUMAC|HARISSA|CHIMICHURRI|ERVAS FINAS|PALMITO|AZEITONA|ANTEPASTO|ALCAPARRA|TOMATE (SECO|PELADO|PASSATA)|PASSATA|COGUMELO|\bATUM|SARDINHA|CONSERVA|HOMUS|HUMMUS|PICLES|KIMCHI|\bPATE\b|CHUTNEY|ALHO|CEBOLA|MOEDOR|MOINHO|CANELA|CRAVO|COMINHO|NOZ MOSCADA|GENGIBRE EM PO|LOURO|ALECRIM|MANJERIC|TOMILHO', 'Azeites, molhos, temperos, antepastos e conservas (padrão da rede)')
r('Gourmet', 'Massas e prontos', r'BROTH|MACARRAO|\bMASSA|ESPAGUETE|SPAGHETTI|PENNE|FUSILLI|TALHARIM|NHOQUE|GNOCCHI|LASANHA|TAGLIATELLE|LINGUINE|FETTUCC|RISOTO|ARROZ ARBORIO|CALDO|SOPA|GRISSIN|TORRADA|BRUSCHET|CROSTINI|MARMITA|CONGELAD|PRONTO|LAMEN|NOODLE|YAKISOBA|\bPAO|\bPAES|WRAP|TORTILHA|PIZZA|QUICHE|SALGADO', 'Massas, risotos, caldos, torradas e prontos (padrão da rede)')
r('Gourmet', 'Bebidas vegetais e básicos', r'YEAST|LEVEDURA|CHOCONUTRI|CHOCO FAMILY|\bACAI\b|CHOCOKI|CREME CULINARIO|EXTRATO (NAT|NATURAL)? ?DE BAUNILHA|EXTRATO NAT|ESSENCIA|AROMA (DE|NATURAL)|SALADA|CHOCOPOPS|\bPOPS\b|BEBIDA (VEGETAL|DE)|LEITE (DE|VEGETAL|EM PO|CONDENSADO|DE COCO)|\bLEITE\b|CREME VEGETAL|CREME DE LEITE|MANTEIGA|\bGHEE\b|ACHOCOLAT|ADOCANTE|XILITOL|ERITRITOL|STEVIA|ESTEVIA|ALULOSE|SUCRALOSE|MONK ?FRUIT|ACUCAR|MELADO|AGAVE|XAROPE DE|OLEO DE (COCO|ABACATE|GERGELIM|GIRASSOL|CANOLA)|OLEO\b|FARINHA|AVEIA|GRANOLA|CEREAL|MUESLI|ARROZ|FEIJAO|LENTILHA|GRAO DE BICO|QUINOA|CHIA|LINHACA|SEMENTE|PROTEINA TEXTURIZADA|PTS\b|TOFU|IOGURTE|QUEIJO|REQUEIJAO|KEFIR|CASTANHA|AMENDOA|\bNOZ|NOZES|AMENDOIM|FRUTA|DAMASCO|TAMARA|UVA PASSA|COCO\b|LEVEDURA|FERMENTO|GELATINA|AGAR|PSYLLIUM', 'Bebidas vegetais, adoçantes, cereais e básicos de despensa (padrão da rede)')
r('Gourmet', 'Biscoitos e snacks', r'ZAYTAS|TORRADIT|BOLINHO|\bBITES\b|BISCOIT|BISCOTT|COOKIE|BOLACHA|ROSQUINHA|WAFER|CRACKER|CHIPS|SNACK|SALGADINHO|PIPOCA|TIRINHA|PALITO|AMENDOIM (JAPONES|CROCANTE)|MIX DE|CROCANTE|BOLO|MUFFIN|MISTURA PARA|PANQUECA|CHURROS|PRETZEL|TORTILLA CHIPS|NACHOS', 'Biscoitos, snacks e misturas para bolo (padrão da rede)')

def classificar(sku):
    x = {'d': nz(sku['desc']) + ' ' + nz(sku.get('marca', '')), 'dep': nz(sku['depto']), 'cat': sku.get('catc') or ''}
    if x['dep'] in ('CAFE', 'ESTOQUE CAFE'):
        return 'Cafeteria da loja', 'Cafeteria', 'Venda da cafeteria da loja, não é produto de gôndola'
    if x['dep'] in ('MATERIAIS LOJAS', 'DESCONHECIDO', 'FRUTAS E VERDURAS'):
        return 'Fora do planograma', 'Materiais e outros', 'Departamento fora da gôndola no cadastro da rede'
    for setor, prat, rx, cond, just in REGRAS:
        if rx.search(x['d']) and (cond is None or cond(x)):
            return setor, prat, just
    CATS = {'9 - PRÉ TREINO': ('Performance', 'Antes do treino'), '23 - ENERGY DRINK': ('Performance', 'Durante o treino'),
            '24 - ENERGY GEL': ('Performance', 'Durante o treino'), '11 - AMINOÁCIDO': ('Performance', 'Depois do treino'),
            '6 - HIPERCALÓRICO': ('Performance', 'Depois do treino'), '27 - CREATINA': ('Creatina', 'Creatina em pó'),
            '19 - TERMOGENICO': ('Peso & Composição Corporal', 'Metabolismo'), '2 - ANTIOXIDANTE': ('Longevidade Saudável', 'Antioxidantes'),
            '5 - IMUNIDADE': ('Imunidade', 'Fitoterápicos'), '13 - PROTEÍNAS VEGANAS': ('Proteínas', 'Veganas'),
            '4 - WHEY PROTEIN': ('Proteínas', 'Whey'), '2 - PROTEINA': ('Proteínas', 'Whey')}
    if x['cat'] in CATS:
        return CATS[x['cat']] + ('Categoria do cadastro da rede (' + x['cat'] + ') levada ao setor correspondente',)
    if x['dep'] in SUPL_DEP:
        return 'A classificar', 'Suplemento sem regra', 'Suplemento sem ativo reconhecido: conferir na revisão'
    return 'A classificar', 'Alimento sem regra', 'Alimento sem tipo reconhecido: conferir na revisão'

if __name__ == '__main__':
    s = pd.read_pickle(R / 'analise/skus_cad.pkl')
    s['catc'] = s['catc'].where(s['catc'] != '(sem)', '')
    res = [classificar(row) for row in s.to_dict('records')]
    s['setor'], s['prateleira'], s['justificativa'] = zip(*res)
    s['origem'] = 'Regra'
    regra = s[['setor', 'prateleira']].copy()
    # Ajustes da revisão item a item (analise/ajustes_manuais.csv: sku,setor,prateleira,motivo) vencem a regra
    aj = R / 'analise/ajustes_manuais.csv'
    if aj.exists():
        a = pd.read_csv(aj, dtype=str).drop_duplicates('sku', keep='last').set_index('sku')
        m = s.sku.astype(str).isin(a.index)
        k = s.loc[m, 'sku'].astype(str)
        s.loc[m, 'setor'] = k.map(a.setor).values
        s.loc[m, 'prateleira'] = k.map(a.prateleira).values
        corr = k.map(a.acao).values == 'corrigido'
        idx = s.index[m]
        s.loc[idx[corr], 'justificativa'] = k[corr].map(a.motivo).values
        s.loc[idx[corr], 'origem'] = 'Corrigido na revisão item a item'
        s.loc[idx[~corr], 'origem'] = 'Regra conferida item a item'
        # conferido com regra que mudou depois da revisão: vale o que foi conferido
        dif = idx[~corr][(regra.loc[idx[~corr], 'setor'] != s.loc[idx[~corr], 'setor']).values | (regra.loc[idx[~corr], 'prateleira'] != s.loc[idx[~corr], 'prateleira']).values]
        s.loc[dif, 'justificativa'] = 'Conferido na revisão item a item'
        print('conferidos em que a regra mudou depois:', len(dif))
        print('ajustes manuais aplicados:', int(m.sum()))
    # Cafés funcionais (café com cafeína extra, TCM, proteína ou colágeno, vendido como suplemento) vão para Performance:
    # a ficha de Performance da rede lista a marca Caffeine (Supercoffee). Café especial torrado continua em Gourmet.
    FUNC_MARCAS = {'CAFFEINE ARMY', 'PLANTPOWER', 'ELEMENTO PURO', 'MAHTA', 'VITAFOR', 'SUPER NUTRITION', 'NUTRATA', 'TOPWAY',
                   'PURAVIDA', 'SANAVITA', 'DOBRO', 'SHARK PRO', 'ADA', 'SOU FIT', 'MUSHIN', 'ESSENTIAL NUTRITION', 'EQUALIV', 'TRUE SOURCE', 'NUTRIFY'}
    cafe = s.setor.eq('Gourmet') & s.prateleira.eq('Cafés, vinhos e presenteáveis') & (
        s.marca.isin(FUNC_MARCAS) | s.desc.str.contains(r'SUPERCOFFEE|ULTRACOFFEE|CAPPUCCINOFIT|V-COFFEE|COFFEE.*(?:PROTEIN|COLLAGEN|TCM|MCT)|\bFIT\b.*CAPPUC', regex=True)
    ) & ~s.desc.str.contains(r'VINHO|ESPUMANTE|PANETONE|CESTA|\bKIT\b', regex=True)
    s.loc[cafe, ['setor', 'prateleira']] = ['Performance', 'Cafés funcionais']
    s.loc[cafe, 'justificativa'] = 'Café funcional vendido como suplemento: a ficha de Performance da rede lista a marca Caffeine (Supercoffee); prateleira própria proposta para a rede validar'
    print('cafés funcionais levados a Performance:', int(cafe.sum()))
    s['tipo'] = s.setor.map(lambda v: 'Proposta 75 LAB' if v in PROPOSTA else ('Fora dos setores' if v in FORA else 'Árvore da rede'))
    s.to_pickle(R / 'analise/classificacao.pkl')
    t = s.groupby(['setor']).agg(skus=('sku', 'count'), valor=('valor', 'sum')).sort_values('valor', ascending=False)
    t['pct'] = (t.valor / t.valor.sum() * 100).round(1)
    t['valor'] = (t.valor / 1e3).round(0)
    print(t.to_string())
    a = s[s.setor == 'A classificar']
    print('a classificar:', len(a), 'SKUs,', round(a.valor.sum() / s.valor.sum() * 100, 1), '% da venda')
