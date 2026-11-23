import { test } from 'node:test';
import assert from 'node:assert/strict';
import { deploymentConfig } from './configure-vercel.mjs';

test('creates a direct API rewrite without losing framework/build configuration', () => {
  const result = deploymentConfig({ framework: 'react-router', buildCommand: 'build', rewrites: [{ source: '/docs', destination: '/help' }] }, 'https://portfolio-api.onrender.com/api/v1');
  assert.deepEqual(result.rewrites[0], { source: '/api/v1/:path*', destination: 'https://portfolio-api.onrender.com/api/v1/:path*' });
  assert.equal(result.framework, 'react-router');
  assert.equal(result.buildCommand, 'build');
  assert.equal(result.rewrites[1].source, '/docs');
  assert.deepEqual(deploymentConfig(result, 'https://portfolio-api.onrender.com'), result);
});
test('rejects placeholder, credentials and non-public deployment destinations', () => {
  for (const value of ['', 'http://example.com', 'https://user:secret@example.com', 'https://YOUR-API.onrender.com', 'https://localhost', 'https://127.0.0.1', 'https://example.com/wrong-path', 'https://example.com/?secret=value']) {
    assert.throws(() => deploymentConfig({}, value));
  }
});
