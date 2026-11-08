#!/usr/bin/env python3
"""Valida e grava temporariamente credencial de implantação SOMENTE da homologação."""
import json
import os
from pathlib import Path
import sys

project = os.environ.get("FDO_HOMOLOG_FIREBASE_PROJECT_ID", "").strip()
raw = os.environ.get("FDO_HOMOLOG_FIREBASE_SERVICE_ACCOUNT", "")
web = os.environ.get("FDO_HOMOLOG_FIREBASE_WEB_CONFIG", "")
if not project or not raw or not web:
    sys.exit("CONFIGURAÇÃO PENDENTE: definir as 2 Variables e 1 Secret FDO_HOMOLOG_ no GitHub antes de publicar.")
try:
    account = json.loads(raw)
    config = json.loads(web)
except ValueError:
    sys.exit("HOMOLOGAÇÃO BLOQUEADA: credencial ou configuração Firebase inválida.")
if (
    project == "producaofolhadosdouro-b6fb5"
    or account.get("type") != "service_account"
    or account.get("project_id") != project
    or config.get("projectId") != project
):
    sys.exit("HOMOLOGAÇÃO BLOQUEADA: credencial e configuração Web devem apontar para o mesmo projeto, diferente da produção.")
if not isinstance(account.get("private_key"), str) or not account.get("client_email"):
    sys.exit("HOMOLOGAÇÃO BLOQUEADA: JSON de conta de serviço incompleto.")
runner = Path(os.environ.get("RUNNER_TEMP", "/tmp"))
path = runner / "fdo-homolog-firebase-sa.json"
path.write_text(raw, encoding="utf-8")
path.chmod(0o600)
print("Credencial de homologação validada: SOMENTE projeto " + project)
print("Credencial temporária preparada com permissões restritas.")
