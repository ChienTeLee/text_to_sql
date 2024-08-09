const http = require('http');

module.exports = {
  devServer: {
    proxy: {
      '/ask_llm/': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        onProxyReq: (proxyReq, req, res) => {
          if (req.method === 'POST') {
            let body = '';
            req.on('data', chunk => {
              body += chunk.toString();
            });
            req.on('end', () => {
              console.log('Request URL:', req.url);
              console.log('Request Method:', req.method);
              console.log('Request Body:', body);
            });
          }
        }
      }
    }
  }
};