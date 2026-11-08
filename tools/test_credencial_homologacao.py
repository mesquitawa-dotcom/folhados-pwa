#!/usr/bin/env python3
"""Verifica que o deploy falha fechado fora do destino e identidade autorizados."""
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest

SCRIPT = Path(__file__).with_name("preparar_credencial_homologacao.py")
class IsolamentoDeploy(unittest.TestCase):
    def setUp(self):
        self.cfg = dict(apiKey="fake-test-key", authDomain="fdo-homologacao-mesquita.firebaseapp.com",
            databaseURL="https://fdo-homologacao-mesquita-default-rtdb.firebaseio.com",
            projectId="fdo-homologacao-mesquita", messagingSenderId="86853323751",
            appId="1:86853323751:web:d971b48a800f71ddadcb42")
        self.env = dict(os.environ, FDO_HOMOLOG_FIREBASE_PROJECT_ID=self.cfg["projectId"],
            GITHUB_REPOSITORY="mesquitawa-dotcom/folhados-pwa", GITHUB_REF="refs/heads/homologacao")
    def run_guard(self, raw=None):
        env = dict(self.env, FDO_HOMOLOG_FIREBASE_WEB_CONFIG=json.dumps(self.cfg) if raw is None else raw)
        return subprocess.run([sys.executable, str(SCRIPT)], env=env, capture_output=True, text=True)
    def test_homologacao(self):
        self.assertEqual(self.run_guard().returncode, 0)
    def test_producao(self):
        self.env["FDO_HOMOLOG_FIREBASE_PROJECT_ID"] = "producaofolhadosdouro-b6fb5"
        self.assertNotEqual(self.run_guard().returncode, 0)
    def test_main(self):
        self.env["GITHUB_REF"] = "refs/heads/main"
        self.assertNotEqual(self.run_guard().returncode, 0)
    def test_outro_repositorio(self):
        self.env["GITHUB_REPOSITORY"] = "outro/folhados-pwa"
        self.assertNotEqual(self.run_guard().returncode, 0)
    def test_banco_trocado(self):
        self.cfg["databaseURL"] = "https://fdo-homologacao-mesquita-outro.firebaseio.com"
        self.assertNotEqual(self.run_guard().returncode, 0)
    def test_app_trocado(self):
        self.cfg["appId"] = "1:86853323751:web:outro"
        self.assertNotEqual(self.run_guard().returncode, 0)
    def test_json_invalido(self):
        self.assertNotEqual(self.run_guard("{").returncode, 0)
    def test_config_ausente(self):
        self.assertNotEqual(self.run_guard("").returncode, 0)
    def test_config_producao(self):
        self.cfg["projectId"] = "producaofolhadosdouro-b6fb5"
        self.assertNotEqual(self.run_guard().returncode, 0)

if __name__ == "__main__":
    unittest.main()
