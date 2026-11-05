# Telas que ficam fora do book de 50 telas. O conteúdo continua em src/ e em fonte/aulas.py:
# para trazer uma tela de volta, basta tirar o título (data-titulo) desta lista e rodar o build.
import re
CORTAR = [
 # capas de capítulo: a barra do topo e o sumário já mostram onde se está
 'Contexto', 'Capítulo 1', 'Capítulo 2', 'Capítulo 3', 'Capítulo 4',
 # aulas de conceito
 'Para entender: Posicionamento', 'Para entender: Curva de valor', 'Para entender: Motivos de compra',
 'Para entender: Árvore de decisão', 'Para entender: Papéis de categoria', 'Para entender: Curva 80/20 e cauda',
 'Para entender: Núcleo e parte local', 'Para entender: Item de referência', 'Para entender: Fluxo da loja',
 'Para entender: Espaço e venda', 'Para entender: Como o olho lê a gôndola', 'Para entender: Como ler um planograma',
 'Para entender: Teste com grupo de controle', 'Para entender: Os números do varejo', 'Para entender: Difusão da novidade',
 # já estão na apresentação executiva
 'A jornada de compra', 'Como a loja fica', 'Como fica a venda', 'As cinco escolhas', 'As peças na gôndola', 'Ponta e mesa na loja', 'O ganho de cada um', 'O calendário',
 # método e exemplos: parte está no manual e no kit, e parte só aqui em src/, como o plano com as marcas e a jornada
 'O que a marca já diz', 'Razão 5: o espaço já existe', 'O que ainda precisa ser testado', 'As regras da rede',
 'Como funciona a gestão de categoria', 'Como ela escolhe', 'O papel de cada categoria', 'O filtro de curadoria',
 'Exemplo: o atendimento', 'Granel: a parede de 20 tubos', 'Por onde começa o empório', 'Exemplo: chegou um produto novo',
 'O plano com as marcas', 'Três papéis de preço', 'A loja inteira em P, M e G', 'O fluxo da cliente',
 'Dividir o espaço', 'Quantas frentes', 'Empório modular', 'Aplicação simulada', 'Biblioteca de peças',
 'Exemplo: lendo as semanas 6 e 12', 'Para a rede andar sozinha', 'Exemplo: uma semana na loja', 'Tudo o que foi combinado', 'Encerramento',
]
def aplicar(telas):
    partes = re.split(r'(?=<section\b)', telas)
    fica, achadas = [], set()
    for p in partes:
        m = re.match(r'<section\b[^>]*data-titulo="([^"]*)"', p)
        if m and m.group(1) in CORTAR:
            achadas.add(m.group(1))
        else:
            fica.append(p)
    falta = set(CORTAR) - achadas
    if falta:
        raise SystemExit(f'telas a cortar não encontradas: {sorted(falta)}')
    return ''.join(fica)
