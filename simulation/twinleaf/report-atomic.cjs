'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');

/**
 * Write a complete report as one locked atomic replacement.
 * The lock is a real exclusive-create filesystem lock, held until rename.
 * A failed writer removes its temporary file and releases its own lock.
 * @param {string} filename
 * @param {unknown} report
 */
function writeReportAtomic(filename,report) {
  assert.ok(typeof filename==='string' && filename.trim(),
    'Report output path required');
  const target=path.resolve(filename);
  const folder=path.dirname(target);
  fs.mkdirSync(folder,{recursive:true});
  const lockPath=target+'.lock';
  const lock=fs.openSync(lockPath,'wx');
  const temporary=target+'.'+process.pid+'.'+Date.now()+'.tmp';
  try {
    fs.writeFileSync(temporary,JSON.stringify(report,null,2)+'\n',
      {encoding:'utf8',flag:'wx'});
    fs.renameSync(temporary,target);
  } finally {
    if(fs.existsSync(temporary))fs.unlinkSync(temporary);
    try{fs.closeSync(lock);}finally{fs.unlinkSync(lockPath);}
  }
}

module.exports={writeReportAtomic};
