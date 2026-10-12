'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const os=require('node:os');
const path=require('node:path');
const {writeReportAtomic}=require('./report-atomic.cjs');

const directory=fs.mkdtempSync(path.join(os.tmpdir(),'tcg-atomic-report-'));
const filename=path.join(directory,'match.json');
try {
  const first={game:'one',counts:[1,2,3]};
  writeReportAtomic(filename,first);
  assert.deepEqual(JSON.parse(fs.readFileSync(filename,'utf8')),first);
  assert.ok(!fs.existsSync(filename+'.lock'));
  console.log('[atomic-report] Fresh JSON report written and lock released.');

  const second={game:'replacement',counts:[4]};
  writeReportAtomic(filename,second);
  assert.deepEqual(JSON.parse(fs.readFileSync(filename,'utf8')),second);
  assert.deepEqual(fs.readdirSync(directory),['match.json']);
  console.log('[atomic-report] Existing report replaced atomically without old temp files.');

  fs.writeFileSync(filename+'.lock','another producer',{flag:'wx'});
  assert.throws(()=>writeReportAtomic(filename,{game:'conflict'}),/EEXIST/);
  assert.deepEqual(JSON.parse(fs.readFileSync(filename,'utf8')),second);
  assert.equal(fs.readFileSync(filename+'.lock','utf8'),'another producer');
  console.log('[atomic-report] Exclusive lock rejects overlapping writer while preserving report.');
} finally {
  fs.rmSync(directory,{recursive:true,force:true});
}
console.log('[atomic-report] PASS: atomic replacement and exclusive lock semantics');
