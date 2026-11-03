# Gera o sprite de ícones (Lucide, licença ISC) a partir da pasta do pacote lucide-static. Grava fonte/icones.svg.
import re,sys,pathlib
L=pathlib.Path(sys.argv[1]);R=pathlib.Path(__file__).resolve().parent
M={'cuidar':'heart-pulse','cesta':'shopping-basket','trigo':'wheat','presente':'gift','tag':'tag','loja':'store','placa':'signpost','camadas':'layers','regua':'ruler','conversa':'message-circle','selo':'badge-check','estrela':'star','gondola':'columns-3','caixa':'credit-card','rede':'network','mercado':'trending-up','teoria':'book-open','alvo':'target','grafico':'chart-column','pessoas':'users','pessoa':'user-round','calendario':'calendar-days','relogio':'clock','escudo':'shield-check','moeda':'circle-dollar-sign','olho':'eye','mao':'hand','livro':'book-marked','regras':'list-checks','caminhao':'truck','pacote':'package','folha':'leaf','lampada':'lightbulb','pergunta':'circle-help','grade':'layout-grid','megafone':'megaphone','chave':'key-round','doc':'file-text','check':'check','aviso':'triangle-alert','local':'map-pin','filtro':'filter','balanca':'scale','ciclo':'refresh-cw','teste':'flask-conical','trofeu':'trophy','porta':'door-open','placa2':'panel-top','prova':'cookie','whey':'dumbbell','pilula':'pill','cafe':'coffee','vinho':'wine','cha':'leaf','azeite':'droplet','carrinho':'shopping-cart','coracao':'heart','mapa':'layout-dashboard','voltar':'repeat','handshake':'handshake','busca':'search','lista':'list','tendencia':'arrow-up-right','lacuna':'circle-dashed','cena':'image'}
s=''
for k,v in M.items():
    f=L/f'{v}.svg'
    if not f.exists(): print('falta',k,v);continue
    t=f.read_text();c=re.search(r'<svg[^>]*>(.*)</svg>',t,flags=re.S).group(1);c=re.sub(r'<!--.*?-->','',c,flags=re.S)
    c=re.sub(r"\s+"," ",c).strip()
    s+=f'<symbol id="i-{k}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">{c}</symbol>'
(R/'icones.svg').write_text(s);print(len(M),len(s))
