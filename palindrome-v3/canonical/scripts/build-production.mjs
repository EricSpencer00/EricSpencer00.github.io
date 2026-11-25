import fs from 'node:fs';import {spawnSync} from 'node:child_process';
const index=fs.readFileSync('index.html'),app=fs.readFileSync('src/App.tsx','utf8');
let status=1;
try {
 fs.copyFileSync('production-template.html','index.html');
 fs.writeFileSync('src/App.tsx',app.replace('"composed on a mac mini"','"composed on a local machine"').replace('"gpt-2 on a mac mini"','"gpt-2 on a local machine"'));
 const result=spawnSync('npm',['run','build','--','--outDir','production-dist'],{stdio:'inherit'});status=result.status??1;
} finally {fs.writeFileSync('index.html',index);fs.writeFileSync('src/App.tsx',app);}
process.exit(status);
