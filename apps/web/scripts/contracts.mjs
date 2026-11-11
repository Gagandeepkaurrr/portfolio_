import {execFileSync} from 'node:child_process';
import {readFileSync,writeFileSync,mkdtempSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import openapiTS,{astToString} from 'openapi-typescript';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../../..');
const temp=mkdtempSync(path.join(tmpdir(),'portfolio-contract-'));
const openapi=path.join(root,'apps/api/openapi.json');
const target=path.join(root,'apps/web/src/lib/generated/api.ts');
try{
 const fresh=path.join(temp,'openapi.json');
 execFileSync('uv',['run','--frozen','python','-m','app.cli','export-openapi',fresh],{cwd:path.join(root,'apps/api'),stdio:'pipe'});
 const schema=readFileSync(fresh,'utf8');
 const code='// Generated from FastAPI OpenAPI. Run pnpm contracts; do not edit.\n'+astToString(await openapiTS(JSON.parse(schema)));
 if(process.argv.includes('--check')){
  if(readFileSync(openapi,'utf8')!==schema||readFileSync(target,'utf8')!==code){console.error('API contract drift detected. Run pnpm contracts and review changes.');process.exitCode=1;}else console.log('OpenAPI and TypeScript contracts are current.');
 }else{writeFileSync(openapi,schema);writeFileSync(target,code);console.log('Generated OpenAPI and TypeScript contracts.');}
}finally{rmSync(temp,{recursive:true,force:true});}
