import {search} from './engine.mjs';
const controllers=new Map();
self.onmessage=async ({data})=>{
  if (data.type==='cancel') {controllers.get(data.id)?.abort();return;}
  if (data.type!=='search') return;
  const controller=new AbortController();controllers.set(data.id,controller);
  try {
    const result=await search(data.options,event=>self.postMessage({id:data.id,...event}),controller.signal);
    self.postMessage({id:data.id,type:'result',result});
  } catch(error) {self.postMessage({id:data.id,type:error.name==='AbortError'?'cancelled':'error',message:error.name==='AbortError'?'Search cancelled.':error.message});}
  finally {controllers.delete(data.id);}
};
