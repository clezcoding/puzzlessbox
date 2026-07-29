import test from 'node:test';
import assert from 'node:assert';
import fs from 'node:fs';
import path from 'node:path';

const tokensPath = path.resolve('brand/tokens.css');

test('tokens.css exists with minimal tracer variables', () => {
  assert.ok(fs.existsSync(tokensPath), 'brand/tokens.css missing');

  const content = fs.readFileSync(tokensPath, 'utf8');
  assert.ok(content.includes('@theme'), 'missing @theme block');
  assert.ok(content.includes('--color-bg'), 'missing --color-bg');
  assert.ok(content.includes('--color-brand'), 'missing --color-brand');
  assert.ok(content.includes('--font-display'), 'missing --font-display');
});
