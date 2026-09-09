"""Patch pontual v26.6.2; somente sobre o snapshot publicado e conferido."""
from pathlib import Path
import hashlib

ROOT = Path.cwd()
p = ROOT / 'index.html'
b = p.read_bytes()
assert hashlib.sha1(b'blob ' + str(len(b)).encode() + b'\0' + b).hexdigest() == 'b7a5f59781bd9195ea4712bd2037ecac2eacc881', 'Base index.html divergente; não aplicar'
s = b.decode('utf-8')
def replace(old, new):
    global s
    assert s.count(old) == 1, ('Âncora deve ser única', old[:90], s.count(old))
    s = s.replace(old, new, 1)
replace("FOLHADOS D'OURO — atualização v26.6.1", "FOLHADOS D'OURO — atualização v26.6.2\n       NOVIDADES v26.6.2:\n       • Corrige o botão de avanço cortado na previsão do porcionamento em telas menores.\n       • Cabeçalho compacto, previsão rolável e Definir Fermento sempre acessível no rodapé.\n       • Receitas, cálculos, voz, navegação e dados preservados.")
replace('.pre-temp-container{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:1.5rem;gap:1rem;text-align:center}', '.pre-temp-container{flex:1;min-height:0;overflow-y:auto;display:flex;flex-direction:column;align-items:center;justify-content:flex-start;padding:.8rem 1rem;gap:1rem;text-align:center}')
replace('.pre-temp-card{background:var(--bg3);border:1px solid var(--brd);border-radius:.6rem;padding:2rem 1.5rem;width:100%;max-width:16rem;box-shadow:0 .4rem 1.5rem rgba(0,0,0,.5)}', '.pre-temp-card{flex-shrink:0;background:var(--bg3);border:1px solid var(--brd);border-radius:.6rem;padding:1.1rem 1rem;width:100%;max-width:16rem;box-shadow:0 .4rem 1.5rem rgba(0,0,0,.5)}\n    /* v26.6.2: ação fora da área rolável; a barra Voltar não pode cortá-la. */\n    #s-pre-temp .start-footer{flex-direction:column;padding:.6rem 1rem;gap:.4rem}\n    #s-pre-temp .start-footer .btn-main{width:100%;min-width:0;padding:.85rem .6rem;font-size:.9rem;letter-spacing:.04rem;line-height:1.3}')
replace('<div id="s-pre-temp" class="scr off">', '<div id="s-pre-temp" class="scr off ux-compact">')
replace('    <button class="btn-main" style="width:auto;min-width:12rem" onclick="escolherTemp()">Definir Fermento →</button>\n  </div>\n  <div class="start-footer">\n    <button class="link-btn" onclick="abrirLotesFarinha()">← Lotes das farinhas</button>', '  </div>\n  <div class="start-footer">\n    <button class="btn-main" id="pre-temp-continuar" onclick="escolherTemp()">Definir Fermento →</button>\n    <button class="link-btn" onclick="abrirLotesFarinha()">← Lotes das farinhas</button>')
replace('Versão 26.6.1 · cache fdo-v26-6-1', 'Versão 26.6.2 · cache fdo-v26-6-2')
replace("versao:'26.6.1'", "versao:'26.6.2'")
p.write_text(s, encoding='utf-8')
p=ROOT/'sw.js'; s=p.read_text(); assert s.count("const CACHE='fdo-v26-6-1'")==1
p.write_text(s.replace("const CACHE='fdo-v26-6-1'", "const CACHE='fdo-v26-6-2'"))
for rel in ('tools/validate_fdo.py','tools/test_v26_6.js'):
 p=ROOT/rel; s=p.read_text(); p.write_text(s.replace("versao:'26.6.1'", "versao:'26.6.2'").replace('VALIDAÇÃO FDO v26.6.1 OK','VALIDAÇÃO FDO v26.6.2 OK').replace("const CACHE='fdo-v26-6-1'", "const CACHE='fdo-v26-6-2'"))
# Só acrescenta o teste de regressão ao job que já tem navegador e Playwright.
p=ROOT/'.github/workflows/validate-fdo.yml';s=p.read_text()
a='      - name: Guardar evidências e telas de teste\n'
assert s.count(a)==1
s=s.replace(a,'      - name: Testar avanço do porcionamento em telas pequenas v26.6.2\n        env:\n          FDO_TEST_ARTIFACT_DIR: /tmp/fdo-usabilidade-tests/porcionamento\n        run: |\n          git show c09b652ad079a02b5bb93fac31d71d61669edde3:index.html > /tmp/fdo-base-v26-6-1.html\n          python tools/test_porcionamento_v26_6_2.py --baseline /tmp/fdo-base-v26-6-1.html\n'+a)
p.write_text(s)
print('Patch v26.6.2 aplicado sobre a base exata; código de produção alterado somente em HTML/CSS e versão de exportação.')
