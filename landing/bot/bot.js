const puppeteer = require('puppeteer');
const axios = require('axios');
const http = require('http');

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';
const FRONTEND_URL = process.env.FRONTEND_URL || 'http://localhost:8000'; 

let isVisiting = false;

async function loginAndVisitAdmin() {
    if (isVisiting) return;
    isVisiting = true;
    console.log('[Bot] Starting admin visit...');
    
    let token;
    try {
        const res = await axios.post(`${BACKEND_URL}/api/login`, {
            username: 'bot',
            password: 'Sup3r_Str0ng_B0t_P4ssw0rd_999!'
        });
        token = res.data.token;
        console.log(`[Bot] Logged in successfully. Token: ${token}`);
    } catch (err) {
        console.error('[Bot] Login failed:', err.response ? err.response.data : err.message);
        isVisiting = false;
        return;
    }

    const browser = await puppeteer.launch({
        args: ['--no-sandbox', '--disable-setuid-sandbox'],
        executablePath: process.env.PUPPETEER_EXECUTABLE_PATH || null
    });
    
    try {
        const page = await browser.newPage();
        
        await page.goto(FRONTEND_URL);
        const frontendUrlObj = new URL(FRONTEND_URL);
        await page.setCookie({
            name: 'token',
            value: token,
            domain: frontendUrlObj.hostname,
            path: '/',
            httpOnly: false
        });

        console.log('[Bot] Visiting admin panel...');
        await page.goto(`${FRONTEND_URL}/admin-support-panel`, { waitUntil: 'networkidle2' });
        
        await new Promise(resolve => setTimeout(resolve, 3000));
        console.log('[Bot] Finished visiting admin panel.');
    } catch (err) {
        console.error('[Bot] Error visiting page:', err.message);
    } finally {
        await browser.close();
        isVisiting = false;
    }
}

const server = http.createServer((req, res) => {
    const url = new URL(req.url, `http://${req.headers.host}`);
    if (url.pathname === '/visit' && url.searchParams.get('secret') === 'AstraBotSecret99') {
        loginAndVisitAdmin();
        res.writeHead(200);
        res.end('Visiting');
    } else {
        res.writeHead(404);
        res.end('Not found');
    }
});

server.listen(3000, () => {
    console.log('[Bot] Listening on port 3000 for triggers');
    loginAndVisitAdmin(); // Visit on startup
});
