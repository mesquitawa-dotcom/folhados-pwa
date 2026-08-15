from pathlib import Path
import json, re

p=Path('index.html')
s=p.read_text(encoding='utf-8')

def once(old,new,label):
    global s
    n=s.count(old)
    if n!=1:
        raise SystemExit(f'{label}: esperado 1 ocorrência, encontrei {n}')
    s=s.replace(old,new,1)

# Versão e descrição.
once("FOLHADOS D'OURO — atualização v25.1\n       NOVIDADES v25.1:",
     "FOLHADOS D'OURO — atualização v25.2\n       NOVIDADES v25.2:\n       • Firebase Authentication identifica o aparelho sem substituir o login do padeiro.\n       • Apenas aparelhos previamente autorizados podem sincronizar dados de produção.\n       • Regras do Realtime Database passam a ser versionadas no GitHub e negam acesso por padrão.\n       NOVIDADES v25.1:", 'cabeçalho v25.2')

# SDK Auth compat, mantendo a mesma versão dos SDKs existentes.
once('  <script src="https://www.gstatic.com/firebasejs/10.13.2/firebase-app-compat.js"></script>\n  <script src="https://www.gstatic.com/firebasejs/10.13.2/firebase-database-compat.js"></script>',
     '  <script src="https://www.gstatic.com/firebasejs/10.13.2/firebase-app-compat.js"></script>\n  <script src="https://www.gstatic.com/firebasejs/10.13.2/firebase-auth-compat.js"></script>\n  <script src="https://www.gstatic.com/firebasejs/10.13.2/firebase-database-compat.js"></script>', 'sdk auth')

# Tela de autorização do aparelho. Não substitui a tela de operador/PIN.
once('<body>\n\n<div id="s-config" class="scr off">', '''<body>

<div id="s-device" class="scr off">
  <div class="geo-wrap">
    <div class="geo-icon">🔐</div>
    <div class="geo-title alert" id="device-title">Autorizar aparelho</div>
    <div class="geo-msg" id="device-msg">Este aparelho ainda não está autorizado a sincronizar a produção.</div>
    <div class="geo-dist" style="word-break:break-all">Código do aparelho<br><b id="device-code">—</b></div>
    <div class="geo-actions">
      <button class="btn-main" onclick="DEVICE.tentarNovamente()">Verificar autorização</button>
      <button class="link-btn" onclick="DEVICE.copiarCodigo()">Copiar código</button>
    </div>
    <div class="cfg-s" style="font-size:.66rem;line-height:1.45;margin-top:.8rem">A autorização do aparelho é separada do login do padeiro. Depois de autorizado, cada operador continua entrando com seu próprio nome e PIN.</div>
  </div>
</div>

<div id="s-config" class="scr off">''', 'tela aparelho')

# Informações do aparelho em Configurações.
once('  <div class="cfg-sep"></div>\n  <div class="cfg-t" style="font-size:1rem">💾 Backup</div>',
     '  <div class="cfg-sep"></div>\n  <div class="cfg-t" style="font-size:1rem">📱 Este aparelho</div>\n  <div class="cfg-s" id="device-info" style="font-size:.68rem;line-height:1.45;word-break:break-all">Identificação Firebase: —</div>\n  <div class="cfg-sep"></div>\n  <div class="cfg-t" style="font-size:1rem">💾 Backup</div>', 'info aparelho config')

# Camada de autenticação/allowlist do aparelho.
anchor='''const FB_SYNC_KEYS=['fdo_lotes','fdo_laminacoes','fdo_lote_seq','fdo_operadores','fdo_farinha_lotes_atuais'];'''
if s.count(anchor)!=1: raise SystemExit('âncora FB_SYNC_KEYS não encontrada')
device_js=r'''// ===== Autorização do aparelho via Firebase Authentication (v25.2) ========
// Identidade do APARELHO é separada da identidade do PADEIRO.
// O padeiro continua escolhendo nome + PIN. O Firebase Auth apenas impede que
// navegadores/aparelhos não cadastrados leiam ou alterem a nuvem.
const DEVICE={
  auth:null, uid:null, registro:null, aprovado:false, localOnly:false,
  iniciado:false, cloudStarted:false, bootLiberado:false, bootCb:null, ref:null,
  cache(){return LS.g('fdo_device_auth_v25',null)},
  nome(){return (this.registro&&this.registro.nome)||('Aparelho '+String(this.uid||LS.g('fdo_device_uid_v25','')).slice(-6).toUpperCase())},
  audit(){return {uid:this.uid||LS.g('fdo_device_uid_v25','')||'',nome:this.nome()}},
  renderConfig(){const el=document.getElementById('device-info');if(!el)return;const u=this.uid||LS.g('fdo_device_uid_v25','')||'—';el.textContent='Firebase: '+u+' · '+(this.aprovado?'autorizado':(this.localOnly?'autorizado anteriormente · offline':'aguardando autorização'));},
  mostrar(msg,titulo){
    const t=document.getElementById('device-title'),m=document.getElementById('device-msg'),c=document.getElementById('device-code');
    if(t)t.textContent=titulo||'Autorizar aparelho';if(m)m.textContent=msg||'Este aparelho ainda não está autorizado.';if(c)c.textContent=this.uid||LS.g('fdo_device_uid_v25','')||'—';
    this.renderConfig();ir('device');
  },
  async copiarCodigo(){const u=this.uid||LS.g('fdo_device_uid_v25','')||'';if(!u)return;try{await navigator.clipboard.writeText(u);alert('Código do aparelho copiado.')}catch(e){alert('Código do aparelho: '+u)}},
  async usuarioRestaurado(){
    if(!this.auth)return null;if(this.auth.currentUser)return this.auth.currentUser;
    return await new Promise(resolve=>{let fim=false,off=null;const done=u=>{if(fim)return;fim=true;try{off&&off()}catch{}resolve(u||null)};off=this.auth.onAuthStateChanged(u=>done(u),()=>done(null));setTimeout(()=>done(this.auth.currentUser),900)});
  },
  liberar(comNuvem){
    if(comNuvem&&!this.cloudStarted){this.cloudStarted=true;SYNC25.init();}
    if(this.bootLiberado)return;this.bootLiberado=true;const cb=this.bootCb;if(typeof cb==='function')cb();
  },
  cacheAprovacao(reg){this.registro=reg||null;this.aprovado=true;this.localOnly=false;LS.s('fdo_device_auth_v25',{uid:this.uid,aprovado:true,nome:(reg&&reg.nome)||'',emTs:Date.now()});this.renderConfig()},
  aplicar(reg){
    this.registro=reg||null;
    if(reg&&reg.ativo===true){this.cacheAprovacao(reg);FB.status('pending','Aparelho autorizado · sincronizando…');this.liberar(true);return}
    this.aprovado=false;this.localOnly=false;try{localStorage.removeItem('fdo_device_auth_v25')}catch{};FB.status('err','⚠ Aparelho não autorizado');
    this.mostrar('Informe este código ao administrador. Depois que o aparelho for autorizado no Firebase, toque em “Verificar autorização”.');
  },
  escutar(){
    if(!FB.db||!this.uid)return;try{this.ref&&this.ref.off&&this.ref.off()}catch{}
    this.ref=FB.db.ref('fdo_dispositivos/'+this.uid);
    this.ref.on('value',snap=>this.aplicar(snap.val()),err=>{console.warn('[DEVICE] autorização',err);if(!navigator.onLine){const c=this.cache();if(c&&c.uid===this.uid&&c.aprovado){this.aprovado=true;this.localOnly=true;this.registro={nome:c.nome||'',ativo:true};FB.status('local','Aparelho autorizado · offline');this.liberar(false);return}}this.mostrar('Não foi possível consultar a autorização deste aparelho. Verifique a internet e tente novamente.','Falha ao validar aparelho')});
  },
  async bootstrap(cb){
    this.bootCb=cb||this.bootCb;if(this.iniciado)return;this.iniciado=true;
    if(typeof firebase==='undefined'||!firebase.initializeApp||!firebase.auth){this.mostrar('O módulo Firebase Authentication não carregou. Recarregue o aplicativo.','Firebase Authentication indisponível');return}
    try{
      if(!firebase.apps.length)firebase.initializeApp(FB_CFG);FB.db=firebase.database();this.auth=firebase.auth();
      let user=await this.usuarioRestaurado();
      if(!user&&navigator.onLine){const cred=await this.auth.signInAnonymously();user=cred.user||this.auth.currentUser}
      if(!user){
        const c=this.cache();if(!navigator.onLine&&c&&c.aprovado){this.uid=c.uid||'';this.registro={nome:c.nome||'',ativo:true};this.aprovado=true;this.localOnly=true;FB.status('local','Aparelho autorizado · offline');this.liberar(false);return}
        this.mostrar('Conecte este aparelho à internet para criar/verificar sua identidade Firebase.','Internet necessária para autorizar');return;
      }
      this.uid=user.uid;try{localStorage.setItem('fdo_device_uid_v25',JSON.stringify(this.uid))}catch{};this.escutar();
    }catch(e){
      console.warn('[DEVICE] bootstrap',e);this.iniciado=false;const c=this.cache();
      if(!navigator.onLine&&c&&c.aprovado){this.uid=c.uid||'';this.registro={nome:c.nome||'',ativo:true};this.aprovado=true;this.localOnly=true;FB.status('local','Aparelho autorizado · offline');this.liberar(false);return}
      const cod=String(e&&e.code||'');const msg=cod.includes('operation-not-allowed')?'Ative o método de login Anônimo no Firebase Authentication antes da publicação.':'Não foi possível autenticar este aparelho no Firebase.';this.mostrar(msg,'Configuração Firebase necessária');
    }
  },
  tentarNovamente(){this.iniciado=false;this.bootstrap(this.bootCb)},
  online(){
    if(this.aprovado&&this.auth&&this.auth.currentUser){if(!this.cloudStarted){this.cloudStarted=true;SYNC25.init()}else FB.aoVoltarOnline();return}
    this.iniciado=false;this.bootstrap(this.bootCb);
  }
};

'''
s=s.replace(anchor,device_js+anchor,1)

# Config mostra identidade e backup registra aparelho, sem alterar conteúdo de produção.
once("  if(typeof renderOpList==='function') renderOpList();\n}\nfunction exportarBackup(){",
     "  if(typeof renderOpList==='function') renderOpList();\n  if(typeof DEVICE!=='undefined') DEVICE.renderConfig();\n}\nfunction exportarBackup(){", 'config render aparelho')
once("  const dados={app:'Folhados d\\'Ouro — Produção',versao:'25.1',exportadoEm:new Date().toISOString(),origem:'localStorage',dados:{}};",
     "  const dados={app:'Folhados d\\'Ouro — Produção',versao:'25.2',exportadoEm:new Date().toISOString(),origem:'localStorage',dispositivo:(typeof DEVICE!=='undefined'?DEVICE.audit():null),dados:{}};", 'backup v25.2')

# Auditoria GPS inclui aparelho, além do padeiro já registrado.
once("        op: op||'?',\n        status: status,",
     "        op: op||'?',\n        dispositivo: (typeof DEVICE!=='undefined'?DEVICE.audit():null),\n        status: status,", 'auditoria GPS aparelho')

# Novos baldes e lotes de laminação guardam o aparelho de criação.
once("    num:seq.num, numOrigem:seq.origem, id:FB.novoId('lote'),\n    receita:st.receita,",
     "    num:seq.num, numOrigem:seq.origem, id:FB.novoId('lote'),\n    dispositivo:(typeof DEVICE!=='undefined'?DEVICE.audit():null),\n    receita:st.receita,", 'aparelho balde')
once("    id:FB.novoId('lam'), nome, seqDia, data:agora.toLocaleString('pt-BR'), dataTs:agora.getTime(),\n    receita, receitaNome, composicao,",
     "    id:FB.novoId('lam'), nome, seqDia, data:agora.toLocaleString('pt-BR'), dataTs:agora.getTime(),\n    dispositivo:(typeof DEVICE!=='undefined'?DEVICE.audit():null),\n    receita, receitaNome, composicao,", 'aparelho laminação')

# SYNC25 só inicia com aparelho aprovado; evita listeners duplicados.
once("  flushing:false, mirrorTimer:{}, mirrorJson:{},",
     "  flushing:false, iniciado:false, mirrorTimer:{}, mirrorJson:{},", 'flag sync iniciado')
once("  init(){\n    if(typeof firebase==='undefined'||!firebase.initializeApp){FB.status('local','Salvo neste aparelho · sem nuvem');return}try{",
     "  init(){\n    if(this.iniciado)return;if(typeof DEVICE!=='undefined'&&!DEVICE.aprovado){FB.status('err','⚠ Aparelho não autorizado');return}this.iniciado=true;\n    if(typeof firebase==='undefined'||!firebase.initializeApp){this.iniciado=false;FB.status('local','Salvo neste aparelho · sem nuvem');return}try{", 'proteção SYNC25')
# Se init lançar antes de conectar, permite nova tentativa.
once("    }catch(e){console.warn('[FB25] init',e);FB.status('err','⚠ Firebase indisponível')}\n  },",
     "    }catch(e){this.iniciado=false;console.warn('[FB25] init',e);FB.status('err','⚠ Firebase indisponível')}\n  },", 'retry SYNC25')

# FB.init passa a representar o bootstrap seguro do aparelho.
once("FB.init=()=>SYNC25.init();", "FB.init=()=>DEVICE.bootstrap(()=>SYNC25.init());", 'override FB.init')

# Conexão voltou: primeiro garante autorização do aparelho.
once("window.addEventListener('online',()=>FB.aoVoltarOnline());",
     "window.addEventListener('online',()=>DEVICE.online());", 'online device')

# Boot: não abre Login/Start até validar o aparelho; offline aprovado continua local.
once("  // Sincronia multi-aparelho via Firebase Realtime Database\n  FB.init();\n  // PIN padrão na primeira execução",
     "  // A sincronização Firebase só inicia depois da autorização do aparelho (v25.2).\n  // O login do padeiro continua separado, por nome + PIN.\n  // PIN padrão na primeira execução", 'remover init antecipado')
once("  GEO.bootstrap(bootApp);\n})();",
     "  DEVICE.bootstrap(()=>GEO.bootstrap(bootApp));\n})();", 'boot seguro')

p.write_text(s,encoding='utf-8')

# Cache PWA.
sw=Path('sw.js').read_text(encoding='utf-8')
if sw.count("const CACHE='fdo-v25-1';")!=1: raise SystemExit('cache v25.1 não encontrado')
sw=sw.replace("const CACHE='fdo-v25-1';","const CACHE='fdo-v25-2';",1)
Path('sw.js').write_text(sw,encoding='utf-8')

# Validador: exige Auth, device gate e regras versionadas.
vp=Path('tools/validate_fdo.py')
v=vp.read_text(encoding='utf-8')
needle="errors=[]\n\ndef fail(msg): errors.append(msg)\n"
if needle not in v: raise SystemExit('âncora validator')
extra="""errors=[]\n\ndef fail(msg): errors.append(msg)\n\n# v25.2 — Firebase Authentication + autorização do aparelho + rules as code\nfor marker in (\"firebase-auth-compat.js\",\"const DEVICE={\",\"fdo_dispositivos/\",\"signInAnonymously\",\"DEVICE.bootstrap(()=>GEO.bootstrap(bootApp))\",\"dispositivo:(typeof DEVICE\"):\n    if marker not in html: fail('v25.2 sem marcador: '+marker)\nfor req in ('database.rules.json','firebase.json'):\n    if not (ROOT/req).exists(): fail('Arquivo Firebase ausente: '+req)\ntry:\n    rules=json.loads((ROOT/'database.rules.json').read_text(encoding='utf-8'))\n    rr=rules.get('rules',{})\n    if rr.get('.read') is not False or rr.get('.write') is not False: fail('Raiz do RTDB deve negar leitura/gravação por padrão')\n    if 'fdo_dispositivos' not in rr or 'fdo_v25' not in rr: fail('Rules sem allowlist de aparelho/v25')\n    if rr.get('fdo_acessos',{}).get('.read') is not False: fail('fdo_acessos não deve ser legível pelo cliente')\nexcept Exception as e: fail('database.rules.json inválido: '+str(e))\ntry:\n    fj=json.loads((ROOT/'firebase.json').read_text(encoding='utf-8'))\n    if fj.get('database',{}).get('rules')!='database.rules.json': fail('firebase.json não aponta para database.rules.json')\nexcept Exception as e: fail('firebase.json inválido: '+str(e))\n"
v=v.replace(needle,extra,1)
vp.write_text(v,encoding='utf-8')

print('Patch segurança v25.2 aplicado')
