from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

def once(old,new,label):
    global s
    n=s.count(old)
    if n!=1:
        raise SystemExit(f'{label}: esperado 1, encontrei {n}')
    s=s.replace(old,new,1)

once("""  liberar(comNuvem){
    if(comNuvem&&!this.cloudStarted){this.cloudStarted=true;SYNC25.init();}
    if(this.bootLiberado)return;this.bootLiberado=true;const cb=this.bootCb;if(typeof cb==='function')cb();
  },""",
"""  liberar(comNuvem){
    if(comNuvem){if(!this.cloudStarted){this.cloudStarted=true;SYNC25.init();}else if(SYNC25.iniciado)FB.aoVoltarOnline();}
    if(this.bootLiberado)return;this.bootLiberado=true;const cb=this.bootCb;if(typeof cb==='function')cb();
  },""", 'liberar')

once("""      if(!firebase.apps.length)firebase.initializeApp(FB_CFG);FB.db=firebase.database();this.auth=firebase.auth();
      let user=await this.usuarioRestaurado();""",
"""      if(!firebase.apps.length)firebase.initializeApp(FB_CFG);FB.db=firebase.database();this.auth=firebase.auth();
      try{await this.auth.setPersistence(firebase.auth.Auth.Persistence.LOCAL)}catch(e){}
      let user=await this.usuarioRestaurado();""", 'persistência auth')

once("""      this.uid=user.uid;try{localStorage.setItem('fdo_device_uid_v25',JSON.stringify(this.uid))}catch{};this.escutar();""",
"""      this.uid=user.uid;try{localStorage.setItem('fdo_device_uid_v25',JSON.stringify(this.uid))}catch{}
      const c=this.cache();if(!navigator.onLine&&c&&c.uid===this.uid&&c.aprovado){this.registro={nome:c.nome||'',ativo:true};this.aprovado=true;this.localOnly=true;FB.status('local','Aparelho autorizado · offline');this.liberar(false);return}
      this.escutar();""", 'boot offline aprovado')

once("""  online(){
    if(this.aprovado&&this.auth&&this.auth.currentUser){if(!this.cloudStarted){this.cloudStarted=true;SYNC25.init()}else FB.aoVoltarOnline();return}
    this.iniciado=false;this.bootstrap(this.bootCb);
  }""",
"""  online(){
    this.localOnly=false;
    if(this.auth&&this.auth.currentUser){this.uid=this.auth.currentUser.uid;this.escutar();return}
    this.iniciado=false;this.bootstrap(this.bootCb);
  }""", 'revalidar ao reconectar')

p.write_text(s,encoding='utf-8')
print('Correção offline/reconexão v25.2 aplicada')
