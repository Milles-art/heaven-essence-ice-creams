// Lightweight static server with gzip compression for the local replica.
// Run with:  node server.js   (or: PORT=4173 node server.js)
const http = require('http');
const fs = require('fs');
const path = require('path');
const zlib = require('zlib');

const ROOT = __dirname;
const PORT = Number(process.env.PORT) || 4173;

const TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.svg': 'image/svg+xml',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.png': 'image/png',
  '.webp': 'image/webp',
  '.woff2': 'font/woff2',
  '.ico': 'image/x-icon',
};

const gzipCache = new Map();

function compressed(file) {
  if (gzipCache.has(file)) return gzipCache.get(file);
  const buf = zlib.gzipSync(fs.readFileSync(file), { level: 9 });
  gzipCache.set(file, buf);
  return buf;
}

http.createServer((req, res) => {
  let pathname;
  try {
    pathname = decodeURIComponent(new URL(req.url, 'http://localhost').pathname);
  } catch {
    res.writeHead(400).end('Bad request');
    return;
  }

  let file = path.join(ROOT, pathname);
  if (!file.startsWith(ROOT)) {
    res.writeHead(403).end('Forbidden');
    return;
  }

  if (fs.existsSync(file) && fs.statSync(file).isDirectory()) {
    file = path.join(file, 'index.html');
  }
  if (!fs.existsSync(file)) {
    file = path.join(ROOT, 'index.html'); // SPA fallback
  }

  const ext = path.extname(file).toLowerCase();
  const type = TYPES[ext] || 'application/octet-stream';
  const textLike = /\.(html|css|js|json|svg|txt|xml)$/i.test(file);
  const acceptsGzip = /\bgzip\b/.test(req.headers['accept-encoding'] || '');

  const headers = {
    'Content-Type': type,
    'Cache-Control': 'no-cache',
  };

  if (textLike && acceptsGzip) {
    headers['Content-Encoding'] = 'gzip';
    headers['Vary'] = 'Accept-Encoding';
    const body = compressed(file);
    res.writeHead(200, headers);
    res.end(body);
  } else {
    const stat = fs.statSync(file);
    headers['Content-Length'] = stat.size;
    res.writeHead(200, headers);
    fs.createReadStream(file).pipe(res);
  }
}).listen(PORT, () => {
  console.log(`Heaven Essence site running (gzip enabled) at http://localhost:${PORT}`);
});
