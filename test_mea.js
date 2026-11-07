// .mea 파서 자체 점검 (실측 파일 없이 만든 가짜 기록): node test_mea.js
const fs = require('fs'), assert = require('assert');
const src = fs.readFileSync(require('path').join(__dirname, 'index.html'), 'utf8');
global.fmtTime = d => (d ? d.toISOString() : '—');
const a = src.indexOf('const MEA_LABELS'), b = src.indexOf("if (typeof module !== 'undefined') module.exports = { parseMEA }");
const parseMEA = new Function(src.slice(a, b) + ';return parseMEA;')();

// field = [type u16][01][name len u32][name][u32 0][tag u16][payload]
const field = (type, tag, payload, name = '') => Buffer.concat([
  Buffer.from([type & 255, type >> 8, 1]), u32(name.length), Buffer.from(name, 'latin1'), u32(0), Buffer.from([tag & 255, tag >> 8]), payload]);
const u32 = n => { const x = Buffer.alloc(4); x.writeUInt32LE(n); return x; };
const f32 = v => { const x = Buffer.alloc(4); x.writeFloatLE(v); return x; };
const f64 = v => { const x = Buffer.alloc(8); x.writeDoubleLE(v); return x; };
const text = s => Buffer.concat([u32(s.length), Buffer.from(s, 'latin1')]);
const arr = v => Buffer.concat([u32(v.length), ...v.map(f32)]);
const record = (named, name, obs, raw) => {
  const n = s => (named ? s : '');
  return Buffer.concat([
    field(0x06b1, 0x00, text(name), n('Sample Name')),
    field(0x0747, 0x03, f64(45623.5), n('Sample time')),      // 2024-11-27 12:00
    field(0x0747, 0x6e, f64(45623.4), n('Alignment time')),   // must not be used as measurement time
    field(0x0630, 0x72, f32(obs)),
    field(0x08c1, 0x2a, u32(1)),                              // dry accessory
    field(0x082f, 0x71, arr(raw)),
    field(0x082f, 0x76, arr([1, 2, 4])),
    field(0x082f, 0x75, arr([40, 60])),
    field(0x0630, 0x7d, f32(2.2)),
    field(0x0630, 0x84, f32(2.5)),
  ]);
};
for (const named of [false, true]) {
  const ms = parseMEA(new Uint8Array(Buffer.concat([Buffer.alloc(20), record(named, 'S1', 1.2, [1, 2, 3]), record(named, 'S2', 7.5, [1, 2, 3])])));
  assert.strictEqual(ms.length, 2, `named=${named}: records`);
  assert.deepStrictEqual(ms.map(m => m.meta.sample), ['S1', 'S2']);
  assert.strictEqual(ms[0].meta.measTime.getHours(), 12, 'measurement time comes from SAMPLE_DATETIME (0x03)');
  assert.deepStrictEqual(ms[0].dist.Q, [0, 40, 100]);
  assert(Math.abs(ms[0].results.Mode - 2.5) < 1e-6 && Math.abs(ms[0].results.Obs - 1.2) < 1e-6);
  assert(ms[1].warnings.some(w => w.includes('차폐율')), 'dry obscuration > 6% warns');
  assert(!ms[0].warnings.some(w => w.includes('차폐율')));
  assert(ms[0].warnings.some(w => w.includes('같은 측정 원자료')), 'same raw sample vector is flagged');
}
console.log('test_mea: OK');
