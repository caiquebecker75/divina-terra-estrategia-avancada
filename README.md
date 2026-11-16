# Divina Terra · Estratégia de trade marketing

Material da 75 LAB, em dois níveis:

- Apresentação executiva, 19 telas, para conduzir a reunião: https://projetos.75lab.com.br/divina-terra-estrategia-avancada/
- Book de 50 telas, com estudos, métodos e planogramas, para consulta: https://projetos.75lab.com.br/divina-terra-estrategia-avancada/book.html
- Manual da estratégia: https://projetos.75lab.com.br/divina-terra-estrategia-avancada/manual.html

Apresentação: editar `fonte/exec/` e rodar `python3 fonte/exec_build.py`, sempre depois do book.
Book: editar `src/` e rodar `python3 fonte/build.py`. `book.html` e `assets/deck.*` são gerados. `fonte/book_cortes.py` lista as telas que ficam fora do book. `fonte/ajustar.mjs` recalcula o tamanho de cada tela; `fonte/revisar.mjs` procura texto cortado.
PDF: `PAGINA=book.html CAPA=pdf-capa-book.html LINK=<link> node fonte/gerar-pdf.mjs <base> divina-terra-book.pdf`, e `PAGINA=index.html node fonte/gerar-pdf.mjs <base> divina-terra-apresentacao.pdf`.
Bases do cliente, análise e kit em planilha ficam fora do Git. Tecla N mostra o roteiro de fala; tecla M abre o sumário.

## Versões

Cada entrega fica congelada em `versoes/vN/`, com selo de versão nas páginas, e a lista fica em
https://projetos.75lab.com.br/divina-terra-estrategia-avancada/versoes/ . A raiz do site é sempre a versão atual.

Ao entregar uma versão nova:

1. Publicar a versão nova na raiz, como de costume.
2. Antes de começar a seguinte, congelar a que foi entregue: `python3 fonte/congelar.py N DD/MM/AAAA [commit]`.
3. Atualizar `fonte/versoes.json` (data, pasta e o que mudou) e rodar `python3 fonte/versoes.py`.

Uma versão congelada não se altera. Os arquivos repetidos entre versões não aumentam o repositório, porque o git guarda uma cópia só.

## v2 (16/11/2026): ordem para gerar a partir da devolutiva

1. `python3 fonte/classificar.py`: setor e prateleira de cada SKU pela árvore de 16 setores da rede (`drive/setores-categorias-dt.html`), com `analise/ajustes_manuais.csv` (revisão item a item) por cima.
2. `python3 fonte/base_v2.py`: grava `analise/vendas5.pkl`, a base que todos os geradores leem.
3. `python3 fonte/cat_base.py` e `python3 fonte/abrangencia.py`: base por setor e papel de cada produto (essencial, complementar, regional, cauda).
4. `python3 fonte/planogramas.py` e, em Python, `planogramas.tudo12()`: planogramas P, M, G e os 12 tipos.
5. `python3 fonte/build.py`, `python3 fonte/exec_build.py`, `python3 fonte/manual.py` e os PDFs.
6. Planilhas para a rede, fora do Git (têm venda): `fonte/planilha_classificacao.py` e `fonte/execucao.py`, em `kit/`.

## Visão estratégica para a diretoria (16/11/2026)

`diretoria.html` e `divina-terra-diretoria.pdf`: 23 slides interativos para a diretoria (fio da história no topo, abas, filtros, simulador; `fonte/diretoria/dir.js`), a partir do deck que o time da rede montou com telas do book. Slides próprios em `fonte/diretoria/novas.html` e `fonte/diretoria/dir.css` (ponto em que estamos, curva de valor, cinco razões, experiência na loja, mini trade book, calendário promocional); os demais vêm de `fonte/exec/telas.html`. Gerar com `python3 fonte/diretoria_build.py`, depois de `exec_build.py`.
