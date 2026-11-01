// Experimental extraction only; never part of production assembly.
const fs=require('fs'),acorn=require('acorn');
const files=fs.readdirSync('src').filter(n=>n.endsWith('.js')&&!n.startsWith('99')).sort();
let omitted=new Set();let out="'use strict';\n",excluded=[];
for(const name of files){let source=fs.readFileSync('src/'+name,'utf8');if(name==='00-foundation.js')source=source.replace('(function(){','');
const tree=acorn.parse(source,{ecmaVersion:'latest'});
for(const n of tree.body){if(n.type==='FunctionDeclaration'){out+=source.slice(n.start,n.end)+'\n';}
else if(n.type==='VariableDeclaration'){for(const d of n.declarations){let s=source.slice(d.start,d.end);if([...omitted].some(id=>new RegExp('\\b'+id+'\\b').test(s))||/document\.|\$\(|window\.|\.getContext\(|new (?:Image|Audio|ResizeObserver)/.test(s)){if(d.id.type==='Identifier')omitted.add(d.id.name.replace(/[^a-zA-Z0-9_]/g,'_'));excluded.push({file:name,declaration:s});continue;}out+=n.kind+' '+s+';\n';}}
else if(n.type==='ExpressionStatement'&&n.expression.type==='AssignmentExpression'&&n.expression.left.type==='Identifier')out+=source.slice(n.start,n.end)+'\n';
else if(n.type==='ExpressionStatement'&&n.expression.type==='CallExpression'&&n.expression.callee.type==='MemberExpression'&&n.expression.callee.property.name==='push')out+=source.slice(n.start,n.end)+'\n';
else if(name==='18-region-charter.js'&&n.type==='ForOfStatement')out+=source.slice(n.start,n.end)+'\n';
else excluded.push({file:name,statement:source.slice(n.start,n.end).slice(0,160)});
}}
fs.writeFileSync('experimental/worker/model.generated.js',out+fs.readFileSync('experimental/worker/runtime-guard.js','utf8')+fs.readFileSync('experimental/worker/adapter.js','utf8')+fs.readFileSync('experimental/worker/root-runtime.js','utf8'));
fs.writeFileSync('experimental/worker/excluded.json',JSON.stringify(excluded,null,2));
