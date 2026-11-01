// Capability check only. Never substitutes a different RNG or edits saved state.
function workerRuntimeArithmetic(){
 const values=JSON.parse('[2147483648,2218605210,4050171023,4294967295]');
 const checks=[];
 for(const value of values){const expectedSigned=value-4294967296;checks.push({op:'unsigned-shift',input:String(value),actual:String(value>>>0),expected:String(value)});checks.push({op:'signed-or',input:String(value),actual:String(value|0),expected:String(expectedSigned)});}
 // Arguments arrive dynamically; avoid relying on folded constant expressions.
 for(const [a,b,expected] of JSON.parse('[[4294967295,5,-5],[2147483648,1,-2147483648],[2147483647,2,-2]]'))checks.push({op:'imul',input:a+','+b,actual:String(Math.imul(a,b)),expected:String(expected)});
 return {ok:checks.every(c=>c.actual===c.expected),checks};
}
function workerRuntimeFallback(page,worker){return !page.ok?'unsupported-runtime':worker?.ok?'worker':'synchronous';}
