#!/usr/bin/env python3
"""Valida a identidade OIDC e o destino exclusivo da homologação; não grava chaves."""
import os
import sys
from build_homologacao import firebase_config

PROJECT = "fdo-homologacao-mesquita"
REPOSITORY = "mesquitawa-dotcom/folhados-pwa"
REF = "refs/heads/homologacao"

def main():
    if os.environ.get("FDO_HOMOLOG_FIREBASE_PROJECT_ID") != PROJECT:
        sys.exit("HOMOLOGAÇÃO BLOQUEADA: projeto diferente do autorizado.")
    if os.environ.get("GITHUB_REPOSITORY") != REPOSITORY or os.environ.get("GITHUB_REF") != REF:
        sys.exit("HOMOLOGAÇÃO BLOQUEADA: repositório ou branch não autorizado.")
    cfg = firebase_config()
    if cfg["databaseURL"].rstrip("/") != "https://" + PROJECT + "-default-rtdb.firebaseio.com":
        sys.exit("HOMOLOGAÇÃO BLOQUEADA: banco diferente do autorizado.")
    if cfg["messagingSenderId"] != "86853323751" or cfg["appId"] != "1:86853323751:web:d971b48a800f71ddadcb42":
        sys.exit("HOMOLOGAÇÃO BLOQUEADA: aplicativo Web diferente do autorizado.")
    print("Destino e identidade da homologação validados. Autenticação temporária OIDC, sem chave privada.")

if __name__ == "__main__":
    main()
