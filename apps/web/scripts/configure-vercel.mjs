import { readFile, writeFile } from 'node:fs/promises';
import { isIP } from 'node:net';
import { URL, fileURLToPath, pathToFileURL } from 'node:url';

export function deploymentConfig(current, input) {
  let api;
  try { api = new URL(input); } catch { throw new Error('Provide the real public HTTPS URL of the Render API.'); }
  if (api.protocol !== 'https:' || api.username || api.password || api.search || api.hash || !['/', '/api/v1', '/api/v1/'].includes(api.pathname) || isIP(api.hostname) || !api.hostname.includes('.') || /^(your-|placeholder)/i.test(api.hostname) || /\.(local|internal)$/.test(api.hostname)) {
    throw new Error('Use a public HTTPS API hostname without credentials, query or fragment, optionally ending in /api/v1.');
  }
  return {
    ...current,
    rewrites: [
      { source: '/api/v1/:path*', destination: `${api.origin}/api/v1/:path*` },
      ...(current.rewrites || []).filter(rule => rule.source !== '/api/v1/:path*'),
    ],
  };
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  try {
    const path = new URL('../vercel.json', import.meta.url);
    const current = JSON.parse(await readFile(path, 'utf8'));
    const config = deploymentConfig(current, process.argv[2] || process.env.API_INTERNAL_URL);
    await writeFile(path, `${JSON.stringify(config, null, 2)}\n`);
    console.log(`Updated ${fileURLToPath(path)} with the direct API rewrite. Commit this file before deploying.`);
  } catch (error) {
    console.error(error.message);
    process.exitCode = 1;
  }
}
