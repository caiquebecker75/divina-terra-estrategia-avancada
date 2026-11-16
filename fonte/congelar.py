# Congela uma versão publicada em versoes/vN, com o selo "Versão N" nas páginas.
# Uso: python3 fonte/congelar.py N DD/MM/AAAA [commit]
# Sem commit, copia o que está publicado agora (HEAD). Depois, acrescente a versão em fonte/versoes.json
# e rode python3 fonte/versoes.py para refazer a página de versões.
import pathlib, subprocess, sys, io, tarfile

R = pathlib.Path(__file__).resolve().parent.parent
n, data = sys.argv[1], sys.argv[2]
commit = sys.argv[3] if len(sys.argv) > 3 else 'HEAD'
dst = R / 'versoes' / f'v{n}'
if dst.exists():
    raise SystemExit(f'{dst} já existe: uma versão congelada não se altera')
tar = subprocess.run(['git', 'archive', commit, '--', '.', ':!fonte', ':!src', ':!versoes', ':!README.md', ':!.gitignore'],
                     cwd=R, capture_output=True, check=True).stdout
dst.mkdir(parents=True)
tarfile.open(fileobj=io.BytesIO(tar)).extractall(dst)

SELO = f'''<style>
#selo-versao{{position:fixed;left:16px;bottom:16px;z-index:99999;display:flex;gap:10px;align-items:center;
 background:#461D17;color:#F7F5F1;font:500 13px/1.2 inherit;padding:9px 14px;border-radius:999px;
 box-shadow:0 0 0 1px rgba(247,245,241,.35),0 4px 14px rgba(70,29,23,.25)}}
#selo-versao a{{color:#E5DDD1;text-decoration:underline;text-underline-offset:3px}}
@media print{{#selo-versao{{display:none}}}}
</style>
<div id="selo-versao">Versão {n} · {data} · arquivada <a href="../index.html">Ver todas as versões</a></div>
<script>if(/[?&]pdf=1/.test(location.search))document.getElementById('selo-versao').remove()</script>
'''
for f in ['index.html', 'book.html', 'manual.html', 'estudo.html']:
    p = dst / f
    if p.exists():
        s = p.read_text()
        assert s.count('</body>') == 1, f
        p.write_text(s.replace('</body>', SELO + '</body>'))
print('congelada em', dst)
