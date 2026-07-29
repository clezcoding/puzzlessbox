import test from 'node:test';
import assert from 'node:assert';
import fs from 'node:fs';
import path from 'node:path';

const assetsDir = path.resolve('brand/assets');

test('apollo-icon-favicon.png exists and is non-empty', () => {
  const filePath = path.join(assetsDir, 'apollo-icon-favicon.png');
  assert.ok(fs.existsSync(filePath), 'apollo-icon-favicon.png missing');

  const stats = fs.statSync(filePath);
  assert.ok(stats.size > 0, 'apollo-icon-favicon.png is empty');
});
