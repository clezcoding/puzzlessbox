import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';

const WORKFLOWS = [
  'deploy-api.yml',
  'deploy-web.yml',
  'deploy-mcp.yml'
];

test('Deploy workflows validation', async (t) => {
  for (const file of WORKFLOWS) {
    await t.test(`Workflow ${file} has no hardcoded Coolify secrets or URLs`, () => {
      const filePath = path.join(process.cwd(), '.github', 'workflows', file);
      const content = fs.readFileSync(filePath, 'utf8');

      // 1. Must contain ${{ secrets.COOLIFY_
      assert.match(
        content,
        /\$\{\{\s*secrets\.COOLIFY_/i,
        `${file} must use COOLIFY secrets`
      );

      // 2. Must NOT contain literal Coolify deploy URL pattern
      const lines = content.split('\n');
      const hexUuidPattern = /[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/i;
      const longHexPattern = /[0-9a-f]{32,}/i;

      for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        
        // Skip lines that define action uses (which use commit SHAs)
        if (line.includes('uses:')) {
          continue;
        }

        // Check for literal Coolify deploy URL patterns
        if (line.includes('coolify') && !line.includes('secrets.COOLIFY_')) {
          assert.ok(
            !/https?:\/\/[^\s"']*coolify/i.test(line),
            `Line ${i + 1} in ${file} contains a literal Coolify URL: ${line.trim()}`
          );
        }
        
        if (/https?:\/\/[^\s"']*/i.test(line)) {
          const urlMatch = line.match(/https?:\/\/[^\s"']*/i);
          if (urlMatch) {
            const url = urlMatch[0];
            assert.ok(
              !url.includes('/deploy'),
              `Line ${i + 1} in ${file} contains a literal deploy URL: ${url}`
            );
          }
        }

        // 3. Must NOT embed a long hex coolify app UUID as a curl target (secrets only)
        assert.ok(
          !hexUuidPattern.test(line),
          `Line ${i + 1} in ${file} contains a hardcoded UUID: ${line.trim()}`
        );
        assert.ok(
          !longHexPattern.test(line),
          `Line ${i + 1} in ${file} contains a long hex string: ${line.trim()}`
        );
      }
    });
  }
});
