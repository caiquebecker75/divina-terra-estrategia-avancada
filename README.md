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
