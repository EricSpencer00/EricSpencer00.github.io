import {exact,normalize} from './engine.mjs';
export class SearchClient {
  constructor(onEvent,workerFactory=()=>new Worker(new URL('./worker.mjs',import.meta.url),{type:'module'})) {
    this.onEvent=onEvent;this.workerFactory=workerFactory;this.sequence=0;this.active=null;this.worker=null;
  }
  cancel(announce=true) {
    if (this.active===null) return;
    this.sequence++;this.active=null;this.worker?.terminate();this.worker=null;
    if (announce) this.onEvent({type:'cancelled',message:'Search cancelled.'});
  }
  request(options) {
    this.cancel(false);
    const id=++this.sequence;this.active=id;
    this.onEvent({type:'status',phase:'starting',message:'Starting phrase search…'});
    try {
      if (!this.worker) this.worker=this.workerFactory();
      const worker=this.worker;
      worker.onmessage=({data})=>{
        if (data.id!==this.active || data.id!==id) return;
        if (data.type==='result') {
          if (!Array.isArray(data.result?.candidates)||data.result.candidates.some(r=>!exact(r.text)||normalize(r.text)!==r.tape)) {
            this.active=null;this.onEvent({type:'error',message:'The result failed its exactness check. Search again.'});return;
          }
          this.active=null;
        } else if (['error','cancelled'].includes(data.type)) this.active=null;
        this.onEvent(data);
      };
      worker.onerror=()=>{
        if (this.active!==id) return;
        this.active=null;worker.terminate();this.worker=null;
        this.onEvent({type:'error',message:'Phrase search could not start. Reload the page and try again.'});
      };
      worker.postMessage({id,type:'search',options});
    } catch {
      this.active=null;this.worker=null;this.onEvent({type:'error',message:'This browser could not start phrase search. Try a current browser.'});
    }
    return id;
  }
}
