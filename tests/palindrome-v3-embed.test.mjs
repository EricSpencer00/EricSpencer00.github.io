import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';
const html=fs.readFileSync(new URL('../palindrome-v3/index.html',import.meta.url),'utf8');
test('preview uses existing canonical generator without finite search controls',()=>{assert.ok(html.includes('src="https://palindrome-webkit-fix.palindrome-3u1.pages.dev/"'));assert.ok(html.includes('title="Palindrome generator"'));assert.ok(!html.includes('settings'));assert.ok(!html.includes('app.mjs'));assert.ok(!html.includes('overhang'));assert.match(html,/noindex/);});
