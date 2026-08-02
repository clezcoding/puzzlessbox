import test from 'node:test';
import assert from 'node:assert';
import fs from 'node:fs';
import path from 'node:path';

const tokensPath = path.resolve('brand/tokens.css');

const semanticColors = [
  '--color-bg',
  '--color-bg-wash',
  '--color-surface',
  '--color-surface-soft',
  '--color-border',
  '--color-border-strong',
  '--color-text',
  '--color-text-muted',
  '--color-primary',
  '--color-primary-hover',
  '--color-brand',
  '--color-brand-soft',
  '--color-accent',
  '--color-accent-soft',
  '--color-cardboard',
  '--color-info',
  '--color-info-soft',
  '--color-destructive',
  '--color-ink-bar',
];

const categoryVars = [
  '--color-inbox-bg',
  '--color-inbox-accent',
  '--color-notes-bg',
  '--color-notes-accent',
  '--color-links-bg',
  '--color-links-accent',
  '--color-tasks-bg',
  '--color-tasks-accent',
  '--color-termine-bg',
  '--color-termine-accent',
];

const fontVars = [
  '--font-display',
  '--font-serif',
  '--font-sans',
  '--font-mono',
];

const spacingVars = [
  '--space-xs',
  '--space-sm',
  '--space-md',
  '--space-lg',
  '--space-xl',
  '--space-2xl',
  '--space-3xl',
];

const textScaleVars = [
  '--text-body',
  '--text-label',
  '--text-heading',
  '--text-display',
  '--text-body-weight',
  '--text-label-weight',
  '--text-heading-weight',
  '--text-display-weight',
  '--text-body-leading',
  '--text-label-leading',
  '--text-heading-leading',
  '--text-display-leading',
];

test('tokens.css defines full light + dark token set', () => {
  assert.ok(fs.existsSync(tokensPath), 'brand/tokens.css missing');

  const content = fs.readFileSync(tokensPath, 'utf8');
  assert.ok(content.includes('@theme'), 'missing light @theme block');
  assert.ok(content.includes('@theme dark'), 'missing @theme dark block');

  for (const variable of [...semanticColors, ...categoryVars, ...fontVars, ...spacingVars, ...textScaleVars]) {
    assert.ok(content.includes(variable), `missing CSS variable: ${variable}`);
  }
});
