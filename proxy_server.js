// 前端托管 + API 代理：解决浏览器访问后端的跨域(CORS)问题
// 用法：node proxy_server.js  然后浏览器打开 http://localhost:8080
// 原理：本服务同时提供 ① 前端 HTML 页面 ② 把 /api/ 等请求转发到后端，
//       浏览器全程只跟 localhost 通信，不存在跨域，后端无需任何改动。
//
// 后端地址配置（三选一，按优先级）：
//   1) 环境变量：BACKEND_TARGET=http://192.168.x.x:8000 node proxy_server.js
//   2) 命令行参数：node proxy_server.js http://192.168.x.x:8000
//   3) 下方 TARGET 默认值（按需修改）
const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = 8080;
const DEFAULT_TARGET = 'http://127.0.0.1:8000'; // 默认本地后端，按实际环境修改或用参数覆盖
const TARGET = process.env.BACKEND_TARGET || process.argv[2] || DEFAULT_TARGET;
const HTML_FILE = path.join(__dirname, 'indoor_map_final_backup_20260729_0921.html');

const server = http.createServer((req, res) => {
  const url = (req.url || '/').split('?')[0];

  // 前端页面
  if (url === '/' || url.endsWith('.html')) {
    fs.readFile(HTML_FILE, (err, data) => {
      if (err) { res.writeHead(500, { 'Content-Type': 'text/plain; charset=utf-8' }); res.end('找不到前端页面文件'); return; }
      res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
      res.end(data);
    });
    return;
  }

  // 其余（/api/、/docs、/openapi.json 等）转发到后端
  const headers = Object.assign({}, req.headers);
  delete headers.host;   // 后端按 Host 判断时不能带 localhost
  const proxyReq = http.request(TARGET + req.url, { method: req.method, headers: headers }, (proxyRes) => {
    res.writeHead(proxyRes.statusCode, proxyRes.headers);
    proxyRes.pipe(res);
  });
  proxyReq.on('error', (e) => { res.writeHead(502, { 'Content-Type': 'text/plain; charset=utf-8' }); res.end('代理转发失败: ' + e.message); });
  req.pipe(proxyReq);
});

server.listen(PORT, () => {
  console.log('前端页面:   http://localhost:' + PORT);
  console.log('API 转发到: ' + TARGET);
  console.log('浏览器打开上面地址，连接定位后端时地址留空（自动走当前源）即可');
});
