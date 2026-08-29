from pathlib import Path
p=Path(__file__).with_name('apply_v26_4.py')
s=p.read_text(encoding='utf-8')
old="""        if(this.imutavel(nome)){
          const r=await ref.transaction(cur=>cur==null?reg:undefined,undefined,false),remoto=r.snapshot.val();
          if(!this.igual(remoto,reg)){
            ok=false;conflitoHistorico=true;
            console.error('[HISTÓRICO] conflito imutável preservado na nuvem',nome,id,{local:reg,remoto});
            continue;
          }
        }else{"""
new="""        if(this.imutavel(nome)){
          let remoto=(await ref.once('value')).val();
          if(remoto==null){
            try{await ref.set(reg);remoto=reg;}
            catch(gravaErr){remoto=(await ref.once('value')).val();if(!this.igual(remoto,reg))throw gravaErr;}
          }
          if(!this.igual(remoto,reg)){
            ok=false;conflitoHistorico=true;
            console.error('[HISTÓRICO] conflito imutável preservado na nuvem',nome,id,{local:reg,remoto});
            continue;
          }
        }else{"""
if s.count(old)!=1: raise SystemExit('bloco de retry por transaction não encontrado exatamente uma vez')
s=s.replace(old,new,1)
s=s.replace("'conflitoHistorico=false',\"cur=>cur==null?reg:undefined\",'Conflito histórico · registro da nuvem preservado',","'conflitoHistorico=false',\"await ref.once('value')\",\"await ref.set(reg)\",'Conflito histórico · registro da nuvem preservado',",1)
s=s.replace("has(html,\"cur=>cur==null?reg:undefined\",'registro histórico só nasce quando ausente');","has(html,\"let remoto=(await ref.once('value')).val()\",'retry histórico começa lendo o remoto');\nhas(html,\"try{await ref.set(reg);remoto=reg;}\",'registro histórico só tenta criar quando ausente');",1)
p.write_text(s,encoding='utf-8')
print('Retry imutável v26.4 ajustado para leitura + criação protegida pelas Rules')
