#!/usr/bin/env bash
set -u
BASE="https://producaofolhadosdouro-b6fb5-default-rtdb.firebaseio.com"
BAD_ETAG='"0000000000000000000000000000000000000000"'

read_probe(){
  local label="$1" path="$2"
  local code
  code=$(curl -sS -o /dev/null -w '%{http_code}' "$BASE/$path.json" || true)
  printf 'READ  %-34s %s\n' "$label" "$code"
}

write_probe(){
  local label="$1" path="$2" payload="$3"
  local code
  # if-match propositalmente incorreto: 412 = escrita autorizada, MAS NÃO EXECUTADA.
  # 401 = bloqueada por Security Rules. Nenhuma chamada abaixo usa ETag correto.
  code=$(curl -sS -o /dev/null -w '%{http_code}' -X PUT \
    -H "Content-Type: application/json" \
    -H "if-match: $BAD_ETAG" \
    --data-binary "$payload" \
    "$BASE/$path.json" || true)
  printf 'WRITE %-34s %s\n' "$label" "$code"
}

echo '=== FIREBASE RTDB AUDIT — ANÔNIMO / NÃO DESTRUTIVO ==='
echo 'Legenda WRITE: 412=autorizada mas não gravada (ETag inválido); 401=bloqueada pelas regras.'
echo 'Legenda READ: 200=leitura anônima permitida; 401=bloqueada.'
echo

# Caminhos legados usados hoje / ponte de migração.
read_probe  'fdo_lotes'                    'fdo_lotes'
write_probe 'fdo_lotes'                    'fdo_lotes' '[]'
read_probe  'fdo_laminacoes'               'fdo_laminacoes'
write_probe 'fdo_laminacoes'               'fdo_laminacoes' '[]'
read_probe  'fdo_lote_seq'                 'fdo_lote_seq'
write_probe 'fdo_lote_seq'                 'fdo_lote_seq' '0'
read_probe  'fdo_operadores'               'fdo_operadores'
write_probe 'fdo_operadores'               'fdo_operadores' '[]'
read_probe  'fdo_farinha_lotes_atuais'     'fdo_farinha_lotes_atuais'
write_probe 'fdo_farinha_lotes_atuais'     'fdo_farinha_lotes_atuais' '{}'
read_probe  'fdo_acessos'                  'fdo_acessos'
write_probe 'fdo_acessos/<audit>'          'fdo_acessos/__fdo_audit_never_write__' 'null'

# Novos caminhos exigidos pela v25.1.
read_probe  'fdo_v25/lotes'                'fdo_v25/lotes'
write_probe 'fdo_v25/lotes/<id>'           'fdo_v25/lotes/__fdo_audit_never_write__' '{"id":"__fdo_audit_never_write__","num":999999,"criadoTs":1,"receita":"r1","etapas":{}}'
read_probe  'fdo_v25/laminacoes'           'fdo_v25/laminacoes'
write_probe 'fdo_v25/laminacoes/<id>'      'fdo_v25/laminacoes/__fdo_audit_never_write__' '{"id":"__fdo_audit_never_write__","nome":"AUDIT","seqDia":999999,"dataTs":1,"receita":"r1","composicao":[],"totalPartes":0,"temMassaAnterior":false,"etapas":{"laminacao":{"feito":true,"emTs":1}}}'
read_probe  'fdo_v25/meta/lote_seq'        'fdo_v25/meta/lote_seq'
write_probe 'fdo_v25/meta/lote_seq'        'fdo_v25/meta/lote_seq' '1'
read_probe  'fdo_v25/meta/lam_seq'         'fdo_v25/meta/lam_seq'
write_probe 'fdo_v25/meta/lam_seq/<dia>'   'fdo_v25/meta/lam_seq/20990101' '1'
read_probe  'fdo_v25/meta/lote_seq_reset'  'fdo_v25/meta/lote_seq_reset'
write_probe 'fdo_v25/meta/lote_seq_reset'  'fdo_v25/meta/lote_seq_reset' '1'
read_probe  'fdo_v25/meta/schema'           'fdo_v25/meta/schema'
write_probe 'fdo_v25/meta/schema'           'fdo_v25/meta/schema' '1'

# As regras em si devem exigir credencial administrativa.
read_probe  '.settings/rules'              '.settings/rules'
