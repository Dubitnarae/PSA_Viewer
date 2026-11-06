// 혼합 예측 계산 자체 점검: node test_mix.js
const fs = require('fs');
const src = fs.readFileSync(require("path").join(__dirname, "index.html"), 'utf8');
const grab = n => { const i = src.indexOf(`function ${n}(`); let d = 0, j = src.indexOf('{', i); for (; ; j++) { if (src[j] === '{') d++; if (src[j] === '}' && !--d) break; } return src.slice(i, j + 1); };
eval(['underAt', 'fractions', 'unionGrid', 'qOnGrid', 'mixQ', 'toDist', 'dAt', 'dRes', 'volFrac', 'optimizeMix', 'corrOn', 'fixQ'].map(grab).join('\n'));
const assert = require('assert');
// lognormal powders on a log grid
const x = Array.from({ length: 101 }, (_, i) => 0.1 * 10 ** (i * 0.04));
const erf = z => { const t = 1 / (1 + 0.3275911 * Math.abs(z)); const y = 1 - (((((1.061405429 * t - 1.453152027) * t) + 1.421413741) * t - 0.284496736) * t + 0.254829592) * t * Math.exp(-z * z); return z >= 0 ? y : -y; };
const ln = (med, s) => ({ x, Q: x.map(d => 50 * (1 + erf(Math.log(d / med) / (s * Math.SQRT2)))) });
const A = ln(10, 0.4), B = ln(60, 0.3);
// 1) identical powders → mixture equals the powder
const g = unionGrid([A, A]); const same = dRes({ x: g, Q: mixQ([qOnGrid(A, g), qOnGrid(A, g)], [0.3, 0.7]) });
assert(Math.abs(same.D50 - 10) < 0.1, same.D50);
// 2) inverse recovers a known 35/65 mix from its D50 + D10
const G = unionGrid([A, B]), Qs = [qOnGrid(A, G), qOnGrid(B, G)];
const tgt = dRes({ x: G, Q: mixQ(Qs, [0.35, 0.65]) });
const obj = w => { const d = { x: G, Q: mixQ(Qs, w) }; return ((dAt(d, 50) / tgt.D50 - 1) * 100) ** 2 + ((dAt(d, 10) / tgt.D10 - 1) * 100) ** 2; };
let best = optimizeMix([1, 1], obj);
assert(Math.abs(best.w[0] - 0.35) < 0.005, best.w);
// 3) stock cap respected: A ≤ 20%
best = optimizeMix([0.2, 1], obj);
assert(best.w[0] <= 0.2 + 1e-9 && Math.abs(best.w[0] + best.w[1] - 1) < 1e-9, best.w);
// 4) density: 50/50 by mass, rho 1 vs 3 → volume 75/25
assert(Math.abs(volFrac([0.5, 0.5], [1, 3])[0] - 0.75) < 1e-9);
assert(volFrac([0.5, 0.5], [1, undefined])[0] === 0.5);
// 5) 3 powders, fraction target
const C = ln(30, 0.2), G3 = unionGrid([A, B, C]), Q3 = [A, B, C].map(d => qOnGrid(d, G3));
const t3 = fractions({ x: G3, Q: mixQ(Q3, [0.2, 0.3, 0.5]) }, [15, 45]);
const t0 = performance.now();
best = optimizeMix([1, 1, 1], w => fractions({ x: G3, Q: mixQ(Q3, w) }, [15, 45]).reduce((a, v, i) => a + (v - t3[i]) ** 2, 0));
assert(best.v < 0.01, best);
// 6) 보정: 실측(=예측보다 굵은 혼합분말)으로 기록 1건 저장하면 같은 혼합의 보정 예측이 실측과 같아짐
const pred = { x: G, Q: mixQ(Qs, [0.35, 0.65]) }, meas = ln(14, 0.45), Gm = unionGrid([pred, meas]);
const rec = { x: Gm, dQ: Gm.map(d => underAt(meas, d) - underAt(pred, d)) };
const fixed = { x: G, Q: fixQ(pred.Q, corrOn(G, [rec])) };
assert(Math.abs(dAt(fixed, 50) / dAt(meas, 50) - 1) < 0.01, [dAt(fixed, 50), dAt(meas, 50)]);
assert(fixed.Q.every((v, i) => v >= 0 && v <= 100 && (!i || v >= fixed.Q[i - 1])));
assert(fixQ(pred.Q, null) === pred.Q);
console.log('ok', best.w.map(v => v.toFixed(3)), (performance.now() - t0).toFixed(0) + 'ms');
