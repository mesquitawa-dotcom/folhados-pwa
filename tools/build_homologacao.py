#!/usr/bin/env python3
"""Constrói somente os arquivos estáticos de homologação com Firebase separado.

Uso: FDO_HOMOLOG_FIREBASE_WEB_CONFIG='{"apiKey":...}' python3 tools/build_homologacao.py
Nenhum arquivo de código fonte é alterado. Falha se tentar usar o Firebase de produção.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import shutil
import sys
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "dist-homologacao"
PRODUCTION_PROJECT = "producaofolhadosdouro-b6fb5"
MANDATORY = ("apiKey", "authDomain", "databaseURL", "projectId", "messagingSenderId", "appId")


def fail(message: str) -> None:
    raise SystemExit("HOMOLOGAÇÃO BLOQUEADA: " + message)


def firebase_config() -> dict:
    raw = os.environ.get("FDO_HOMOLOG_FIREBASE_WEB_CONFIG", "").strip()
    if not raw:
        fail("falta variável FDO_HOMOLOG_FIREBASE_WEB_CONFIG do projeto Firebase exclusivo de testes")
    try:
        cfg = json.loads(raw)
    except json.JSONDecodeError:
        fail("a configuração do Firebase de homologação não é um JSON válido")
    if not isinstance(cfg, dict) or any(not isinstance(cfg.get(k), str) or not cfg[k].strip() for k in MANDATORY):
        fail("faltam campos obrigatórios na configuração Firebase Web (apiKey, authDomain, databaseURL, projectId, messagingSenderId, appId)")
    project = cfg["projectId"]
    expected_project = os.environ.get("FDO_HOMOLOG_FIREBASE_PROJECT_ID", "").strip()
    if expected_project and expected_project != project:
        fail("o projectId da configuração Web diverge do projeto de homologação autorizado")
    if project == PRODUCTION_PROJECT or not re.fullmatch(r"[a-z][a-z0-9-]{4,50}", project):
        fail("ID de projeto inválido ou igual ao Firebase real de produção")
    if cfg["authDomain"] != project + ".firebaseapp.com":
        fail("authDomain não corresponde ao projeto de homologação")
    db_host = urlparse(cfg["databaseURL"]).hostname
    if not db_host or project not in db_host or not db_host.endswith((".firebaseio.com", ".firebasedatabase.app")):
        fail("databaseURL não pertence ao projeto de homologação")
    if PRODUCTION_PROJECT in raw:
        fail("configuração de teste contém identificadores do projeto de produção")
    return cfg


def replace_js_const(source: str, name: str, replacement: str, *, is_object: bool) -> str:
    suffix = r"\{[\s\S]*?\};" if is_object else r"(?:'[^']*'|\"[^\"]*\");"
    pattern = re.compile(r"(const\s+" + re.escape(name) + r"\s*=\s*)" + suffix)
    updated, n = pattern.subn(lambda m: m.group(1) + replacement + ";", source)
    if n != 1:
        fail(f"esperado exatamente 1 parâmetro {name}; encontrados {n}")
    return updated


def inject_banner(html: str, *, title: str) -> str:
    banner = (
        '<div role="status" aria-label="Ambiente de homologação" '
        'style="position:sticky;top:0;z-index:100000;background:#6b210b;'
        'border-bottom:2px solid #ffd966;color:#fff;padding:9px 12px;'
        'text-align:center;font:700 15px Arial,sans-serif">'
        '⚠ HOMOLOGAÇÃO · USE SOMENTE DADOS FICTÍCIOS · NÃO É PRODUÇÃO</div>'
    )
    html, n = re.subn(r"<body(\s[^>]*)?>", lambda m: m.group(0) + banner, html, count=1, flags=re.I)
    if n != 1:
        fail(f"não foi possível colocar aviso permanente no {title}")
    html = re.sub(r"(<head[^>]*>)", r'\1<meta name="robots" content="noindex,nofollow,noarchive">', html, count=1, flags=re.I)
    return html


def main() -> None:
    cfg = firebase_config()
    if DEST.is_symlink():
        fail("destino dist-homologacao é um symlink")
    if DEST.exists():
        shutil.rmtree(DEST)
    DEST.mkdir(parents=True)
    worker_src = (ROOT / "sw.js").read_text(encoding="utf-8")
    assets = re.search(r"const\s+ASSETS\s*=\s*\[([\s\S]*?)\];", worker_src)
    if not assets:
        fail("array ASSETS não encontrado no Service Worker")
    rel_paths = {"index.html", "sw.js"}
    for path in re.findall(r"""['"](\./[^'"]+)['"]""", assets.group(1)):
        if path != "./":
            rel_paths.add(path.removeprefix("./"))
    for rel in sorted(rel_paths):
        candidate = ROOT / rel
        if not candidate.is_file() or ".." in Path(rel).parts:
            fail("recurso obrigatório ausente ou inseguro: " + rel)
        target = DEST / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(candidate, target)
    if "ponto.html" in rel_paths and "ponto.js" not in rel_paths:
        fail("Ponto declarado sem seu JavaScript")

    cfg_literal = json.dumps(cfg, ensure_ascii=True, separators=(",", ":"))
    site_key = os.environ.get("FDO_HOMOLOG_APP_CHECK_KEY", "").strip()
    if site_key and not re.fullmatch(r"[A-Za-z0-9_-]{15,130}", site_key):
        fail("chave pública App Check inválida")
    appcheck_literal = json.dumps(site_key, ensure_ascii=True)

    index = (DEST / "index.html").read_text(encoding="utf-8")
    index = replace_js_const(index, "FB_CFG", cfg_literal, is_object=True)
    index = replace_js_const(index, "APP_CHECK_SITE_KEY", appcheck_literal, is_object=False)
    (DEST / "index.html").write_text(inject_banner(index, title="index.html"), encoding="utf-8")

    ponto_js = DEST / "ponto.js"
    if ponto_js.exists():
        js = ponto_js.read_text(encoding="utf-8")
        js = replace_js_const(js, "PONTO_FIREBASE_CFG", cfg_literal, is_object=True)
        js = replace_js_const(js, "PONTO_APP_CHECK_KEY", appcheck_literal, is_object=False)
        ponto_js.write_text(js, encoding="utf-8")
        html = DEST / "ponto.html"
        if not html.exists():
            fail("ponto.js existe mas ponto.html está ausente")
        html.write_text(inject_banner(html.read_text(encoding="utf-8"), title="ponto.html"), encoding="utf-8")

    sw = (DEST / "sw.js").read_text(encoding="utf-8")
    sw, n = re.subn(r"(const\s+CACHE\s*=\s*['\"])([^'\"]+)(['\"])", r"\1homolog-\2\3", sw, count=1)
    if n != 1:
        fail("não foi possível nomear o cache de homologação")
    (DEST / "sw.js").write_text(sw, encoding="utf-8")

    for rel in ("index.html", "ponto.js"):
        file = DEST / rel
        if file.exists():
            content = file.read_text(encoding="utf-8")
            if PRODUCTION_PROJECT in content:
                fail(f"{rel} ainda referencia o Firebase de produção")
    assert cfg["projectId"] not in (PRODUCTION_PROJECT, "")
    print("HOMOLOGAÇÃO OK: saída estática preparada para projeto Firebase separado, sem modificar o código fonte.")
    print("PROJETO AUTORIZADO: " + cfg["projectId"])


if __name__ == "__main__":
    main()
