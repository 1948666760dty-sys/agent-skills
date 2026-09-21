// Validate independently generated replies, not a duplicate marker implementation.
// Usage: node check-observations.cjs observations.json
// Observations: [{name, no_rush_enabled, action: 'execute'|'clarify', messages: ['...']}]
const fs = require('node:fs');
const assert = require('node:assert/strict');
const path = require('node:path');
const cases = JSON.parse(fs.readFileSync(path.join(__dirname, 'evals.json'), 'utf8')).marker_cases;
const observations = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
assert.ok(Array.isArray(observations), 'observations must be an array');
assert.equal(observations.length, cases.length, 'missing or extra observations');
assert.equal(new Set(observations.map(x => x.name)).size, cases.length, 'duplicate observations');
let failed = 0;
for (const c of cases) {
  try {
    const o = observations.find(x => x.name === c.name);
    assert.ok(o, 'missing observation');
    assert.equal(o.no_rush_enabled, c.observed_contract.no_rush_enabled, 'activation');
    assert.equal(o.action, c.observed_contract.action, 'understanding gate');
    assert.ok(Array.isArray(o.messages) && o.messages.length > 0, 'missing replies');
    assert.ok(o.messages.every(x => typeof x === 'string' && x.trim()), 'empty reply');
    const onCount = o.messages.reduce((n, s) => n + s.split('不着急 ✓').length - 1, 0);
    const offCount = o.messages.reduce((n, s) => n + s.split('不着急 ✗').length - 1, 0);
    const count = onCount + offCount;
    assert.equal(count, c.observed_contract.marker_count, 'status marker count');
    if (count) {
      const expected = o.no_rush_enabled ? '不着急 ✓' : '不着急 ✗';
      const opposite = o.no_rush_enabled ? '不着急 ✗' : '不着急 ✓';
      assert.ok(o.messages[0].trimStart().startsWith(expected), 'correct status marker must precede first prose/progress');
      assert.equal(o.messages.reduce((n, s) => n + s.split(opposite).length - 1, 0), 0, 'opposite status marker must not appear');
    }
    if (c.expect.includes('no_marker_in_final')) {
      assert.ok(o.messages.length >= 2, 'must simulate progress and final');
      assert.ok(!o.messages.at(-1).includes('不着急 ✓') && !o.messages.at(-1).includes('不着急 ✗'), 'duplicate final status marker');
    }
    if (c.observed_contract.question_required) {
      const joined = o.messages.join('\n');
      assert.ok(/[?？]/.test(joined), 'clarification case must visibly ask at least one question');
    }
    if (c.name === 'strict_json_output') {
      assert.equal(o.messages.length, 2, 'strict JSON case must use separate status and payload messages');
      const result = JSON.parse(o.messages.at(-1));
      assert.deepEqual(Object.keys(result), ['steps']);
      assert.ok(Array.isArray(result.steps) && result.steps.length > 0);
    }
    console.log(`PASS ${c.name}`);
  } catch (e) {
    failed++;
    console.error(`FAIL ${c.name}: ${e.message}`);
  }
}
console.log(`${cases.length - failed}/${cases.length} marker observations passed`);
process.exitCode = failed ? 1 : 0;
