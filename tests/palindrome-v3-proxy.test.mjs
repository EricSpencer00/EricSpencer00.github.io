import test from 'node:test';import assert from 'node:assert/strict';
import {onRequest} from '../palindrome-v3/canonical/functions/api/[[path]].js';
test('preview delegates the same v3 request to the existing service and preserves its streamed response',async()=>{
 const original=globalThis.fetch;let requested;const payload=JSON.stringify({version:3,text:'Do geese see God?'});
 globalThis.fetch=async(url,options)=>{requested={url:String(url),options};return new Response(payload,{status:200,headers:{'content-type':'application/json','content-encoding':'gzip','content-length':'999'}});};
 try{const response=await onRequest({request:new Request('https://palindrome-webkit-fix.palindrome-3u1.pages.dev/api/v3/composition?letters=1200&seed=0')});assert.equal(requested.url,'https://palindrome-api.ericspencer.us/api/v3/composition?letters=1200&seed=0');assert.equal(requested.options.method,'GET');assert.equal(await response.text(),payload);assert.equal(response.status,200);assert.equal(response.headers.get('content-encoding'),null);assert.equal(response.headers.get('content-length'),null);}finally{globalThis.fetch=original;}
});
