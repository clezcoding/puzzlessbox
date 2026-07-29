import test from 'node:test';
import assert from 'node:assert';
import fs from 'node:fs';
import path from 'node:path';

const assetsDir = path.resolve('brand/assets');

const expectedAssets = [
  'apollo-icon-app.png',
  'apollo-icon-favicon.png',
  'apollo-icon-dark.png',
  'apollo-wordmark.png',
  'apollo-avatar.png',
  'apollo-empty-inbox.png',
  'apollo-empty-board.png',
  'apollo-empty-caught.png',
  'apollo-empty-notes.png',
  'apollo-empty-links.png',
  'apollo-empty-tasks.png',
  'apollo-empty-cal.png',
  'apollo-og.png',
  'apollo-splash.png',
  'apollo-loading.png',
  'apollo-error.png',
  'apollo-404.png',
  'apollo-offline.png',
  'apollo-capture.png',
  'apollo-onboard.png',
  'apollo-pose-think.png',
  'apollo-pattern.png',
  'apollo-email-header.png',
  'apollo-stickers.png',
  'apollo-notify.png',
];

test('all 25 canonical Apollo PNG assets exist and are non-empty', () => {
  for (const asset of expectedAssets) {
    const filePath = path.join(assetsDir, asset);
    assert.ok(fs.existsSync(filePath), `missing asset: ${asset}`);

    const stats = fs.statSync(filePath);
    assert.ok(stats.size > 0, `empty asset: ${asset}`);
  }

  assert.strictEqual(expectedAssets.length, 25);
});
