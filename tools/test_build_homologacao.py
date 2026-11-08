#!/usr/bin/env python3
"""Teste isolado do empacotador de homologação; nunca se conecta ao Firebase."""
from pathlib import Path
import json
import os
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "dist-homologacao"
CONFIG = {
    "apiKey": "CHAVE_PUBLICA_TESTE",
    "authDomain": "fdo-homologacao-exemplo.firebaseapp.com",
    "databaseURL": "https://fdo-homologacao-exemplo-default-rtdb.firebaseio.com",
    "projectId": "fdo-homologacao-exemplo",
    "storageBucket": "fdo-homologacao-exemplo.firebasestorage.app",
    "messagingSenderId": "1234567890",
    "appId": "1:1234567890:web:testepublico",
}
env = dict(os.environ, FDO_HOMOLOG_FIREBASE_WEB_CONFIG=json.dumps(CONFIG),
           FDO_HOMOLOG_FIREBASE_PROJECT_ID="fdo-homologacao-exemplo")
result = subprocess.run([sys.executable, "tools/build_homologacao.py"],
                        cwd=ROOT, env=env, capture_output=True, text=True)
assert result.returncode == 0, result.stderr + result.stdout
index = (OUT / "index.html").read_text(encoding="utf-8")
ponto = (OUT / "ponto.js").read_text(encoding="utf-8")
html_ponto = (OUT / "ponto.html").read_text(encoding="utf-8")
worker = (OUT / "sw.js").read_text(encoding="utf-8")
assert "fdo-homologacao-exemplo.firebaseapp.com" in index
assert "fdo-homologacao-exemplo.firebaseapp.com" in ponto
assert "producaofolhadosdouro-b6fb5" not in index + ponto
assert "HOMOLOGAÇÃO" in index and "HOMOLOGAÇÃO" in html_ponto
assert "homolog-fdo-v" in worker
assert (OUT / "manifest.json").read_bytes() == (ROOT / "manifest.json").read_bytes()
assert (OUT / "ponto-manifest.json").read_bytes() == (ROOT / "ponto-manifest.json").read_bytes()
assert (OUT / "vendor/firebase-database-compat.js").is_file()
assert not (OUT / ".github").exists()
assert not (OUT / "database.rules.json").exists()
wrong = dict(env, FDO_HOMOLOG_FIREBASE_PROJECT_ID="producaofolhadosdouro-b6fb5")
bad = subprocess.run([sys.executable, "tools/build_homologacao.py"],
                     cwd=ROOT, env=wrong, capture_output=True, text=True)
assert bad.returncode != 0, "Deveria recusar projectId incompatível"
wrong = dict(env, FDO_HOMOLOG_FIREBASE_WEB_CONFIG=json.dumps({
    **CONFIG, "projectId": "producaofolhadosdouro-b6fb5",
    "authDomain": "producaofolhadosdouro-b6fb5.firebaseapp.com",
    "databaseURL": "https://producaofolhadosdouro-b6fb5-default-rtdb.firebaseio.com",
}), FDO_HOMOLOG_FIREBASE_PROJECT_ID="producaofolhadosdouro-b6fb5")
bad = subprocess.run([sys.executable, "tools/build_homologacao.py"],
                     cwd=ROOT, env=wrong, capture_output=True, text=True)
assert bad.returncode != 0, "Deveria recusar o projeto real de produção"
print("TESTE HOMOLOGAÇÃO OK: origem preservada, isolamento de Firebase e falha segura")
