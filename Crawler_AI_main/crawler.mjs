import { chromium } from 'playwright';
import { mkdir, appendFile, stat } from 'fs/promises';
import fetch from 'node-fetch';
import dotenv from 'dotenv';
import pLimit from 'p-limit';
import path from 'path';
import { fileURLToPath } from 'url';

// Configuración de ES modules
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

dotenv.config();

// Variables globales
let fileNumber = 1;
let visitedUrls = new Set();
const MAX_FILE_SIZE = 1.2 * 1024 * 1024; // 1.2 MB
let baseUrl;
let browser;

// Configuración
const CODEGPT_API_KEY = process.env.CODEGPT_API_KEY;
const AGENT_ID = process.env.AGENT_ID;

if (!CODEGPT_API_KEY || !AGENT_ID) {
    console.warn("Advertencia: CODEGPT_API_KEY y AGENT_ID no encontrados en .env - se guardará el contenido sin procesar");
}

// Rate limiting
const limit = pLimit(3);
const rateLimitDelay = () => new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 2000));

// Utilidades
const getCurrentFileSize = async (fileName) => {
    try {
        const stats = await stat(fileName);
        return stats.size;
    } catch (error) {
        if (error.code === 'ENOENT') return 0;
        throw error;
    }
};

const initBrowser = async () => {
    if (!browser) {
        browser = await chromium.launch({
            headless: true,
            args: [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-blink-features=AutomationControlled',
                '--disable-infobars',
                '--window-size=1920,1080',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--disable-gpu'
            ]
        });
    }
    return browser;
};

const closeBrowser = async () => {
    if (browser) {
        await browser.close();
        browser = null;
    }
};

// Análisis de contenido
const analyzeContentWithCodeGPT = async (content) => {
    if (!CODEGPT_API_KEY || !AGENT_ID) {
        return content;
    }

    try {
        const response = await fetch("https://api.codegpt.co/api/v1/chat/completions", {
            method: "POST",
            headers: {
                "Authorization": `Bearer ${CODEGPT_API_KEY}`,
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                agentId: AGENT_ID,
                stream: false,
                format: "json",
                messages: [{
                    role: "user",
                    content: `Analiza y extrae el contenido principal del siguiente texto, 
                             manteniendo títulos, subtítulos y bloques de código. 
                             Elimina contenido irrelevante:\n\n${content}`
                }]
            })
        });

        if (!response.ok) {
            throw new Error(`Error en API: ${response.status}`);
        }

        const data = await response.json();
        return data.choices[0].message.content || content;
    } catch (error) {
        console.error('Error en analyzeContentWithCodeGPT:', error);
        return content;
    }
};


// Extracción de contenido mejorada
const extractContent = async (page) => {
    return await page.evaluate(() => {
        const walkDOM = (node, func) => {
            func(node);
            node = node.firstChild;
            while (node) {
                walkDOM(node, func);
                node = node.nextSibling;
            }
        };

        const isRelevantElement = (node) => {
            const relevantTags = ['P', 'H1', 'H2', 'H3', 'H4', 'H5', 'H6', 'UL', 'OL', 'LI', 'PRE', 'CODE', 'TABLE', 'TR', 'TD', 'TH'];
            return relevantTags.includes(node.nodeName) && !node.closest('script, style, noscript, iframe');
        };

        let textContent = '';
        walkDOM(document.body, function(node) {
            if (node.nodeType === Node.TEXT_NODE && node.textContent.trim() !== '' && isRelevantElement(node.parentNode)) {
                textContent += node.textContent + '\n';
            } else if (isRelevantElement(node)) {
                if (node.nodeName === 'PRE' || node.nodeName === 'CODE') {
                    textContent += node.textContent + '\n\n';
                }
                if (['H1', 'H2', 'H3', 'H4', 'H5', 'H6'].includes(node.nodeName)) {
                    textContent += '\n' + '='.repeat(50) + '\n';
                }
                textContent += '\n';
            }
        });

        return textContent.trim();
    });
};

// Procesamiento de contenido
const processContent = async (content, url) => {
    try {
        const cleanContent = content.trim();
        if (!cleanContent) return null;

        const analyzedContent = await analyzeContentWithCodeGPT(cleanContent);
        return analyzedContent ? {
            url,
            content: analyzedContent,
            timestamp: new Date().toISOString()
        } : null;
    } catch (error) {
        console.error(`Error procesando contenido de ${url}:`, error);
        return null;
    }
};

// Guardado de contenido
const saveContent = async (processedContent) => {
    try {
        const baseDir = path.join('out', new URL(baseUrl).hostname);
        await mkdir(baseDir, { recursive: true });

        const fileName = path.join(baseDir, `${fileNumber}.txt`);
        const currentSize = await getCurrentFileSize(fileName);

        if (currentSize + Buffer.byteLength(processedContent.content) > MAX_FILE_SIZE) {
            fileNumber++;
        }

        const updatedFileName = path.join(baseDir, `${fileNumber}.txt`);
        const formattedContent = `
URL: ${processedContent.url}
Timestamp: ${processedContent.timestamp}

${processedContent.content}

${'='.repeat(80)}
`;

        await appendFile(updatedFileName, formattedContent);
        console.log(`✓ Contenido guardado: ${processedContent.url} -> ${updatedFileName}`);
    } catch (error) {
        console.error('Error guardando contenido:', error);
    }
};

// Función principal de scraping
const scraper = async (url) => {
    if (visitedUrls.has(url) || !url.startsWith(baseUrl)) {
        return;
    }

    console.log(`Procesando: ${url}`);
    visitedUrls.add(url);

    const context = await browser.newContext({
        userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        viewport: { width: 1920, height: 1080 },
        deviceScaleFactor: 1,
    });
    
    const page = await context.newPage();

    try {
        // Configurar timeouts y manejo de errores
        page.setDefaultTimeout(60000);
        page.setDefaultNavigationTimeout(60000);

        // Interceptar y cancelar peticiones innecesarias
        await page.route('**/*', (route) => {
            const request = route.request();
            if (['image', 'stylesheet', 'font'].includes(request.resourceType())) {
                return route.abort();
            }
            return route.continue();
        });

        // Navegar a la página
        await page.goto(url, { 
            waitUntil: 'domcontentloaded',
            timeout: 60000
        });

        // Esperar a que el contenido principal esté disponible
        try {
            await page.waitForSelector('body', { timeout: 30000 });
            // Esperar un poco más para contenido dinámico
            await page.waitForTimeout(2000);
        } catch (error) {
            console.warn(`Advertencia: Timeout esperando el selector en ${url}`);
        }

        // Extraer enlaces
        const links = await page.evaluate((baseUrl) => {
            return Array.from(document.querySelectorAll('a'))
                .map(a => {
                    try {
                        const href = a.href;
                        if (!href) return null;
                        const url = new URL(href);
                        // Limpiar fragmentos y parámetros
                        url.hash = '';
                        url.search = '';
                        return url.href;
                    } catch {
                        return null;
                    }
                })
                .filter((href, index, self) => 
                    href && 
                    href.startsWith(baseUrl) && 
                    self.indexOf(href) === index
                );
        }, baseUrl);

        // Extraer contenido
        let content;
        try {
            content = await Promise.race([
                extractContent(page),
                new Promise((_, reject) => 
                    setTimeout(() => reject(new Error('Timeout extracting content')), 30000)
                )
            ]);
        } catch (error) {
            console.warn(`Advertencia: ${error.message} en ${url}`);
            content = await page.evaluate(() => document.body.innerText);
        }

        const processedContent = await processContent(content, url);

        if (processedContent) {
            await saveContent(processedContent);
        }

        // Procesar enlaces secuencialmente
        for (const link of links) {
            try {
                await scraper(link);
                // Delay aleatorio entre peticiones
                await rateLimitDelay();
            } catch (error) {
                console.error(`Error procesando enlace ${link}:`, error);
                continue;
            }
        }

    } catch (error) {
        console.error(`Error en scraping de ${url}:`, error);
        throw error;
    } finally {
        await page.close();
        await context.close();
    }
};

// Función principal
const main = async () => {
    const startTime = Date.now();
    let exitCode = 0;

    try {
        const url = process.argv[2];
        if (!url) {
            throw new Error('Por favor proporciona una URL como argumento.');
        }

        baseUrl = url.endsWith('/') ? url : url + '/';
        console.log(`Iniciando scraping desde ${baseUrl}`);
        console.log('Configuración inicial...');

        browser = await initBrowser();
        await scraper(baseUrl);

        const duration = (Date.now() - startTime) / 1000;
        console.log(`\nScraping completado exitosamente`);
        console.log(`URLs procesadas: ${visitedUrls.size}`);
        console.log(`Tiempo total: ${duration.toFixed(2)} segundos`);
    } catch (error) {
        console.error('Error en scraping:', error);
        exitCode = 1;
    } finally {
        await closeBrowser();
        process.exit(exitCode);
    }
};

// Manejo de errores y señales
process.on('unhandledRejection', (error) => {
    console.error('Rejection no manejada:', error);
    closeBrowser().then(() => process.exit(1));
});

process.on('SIGINT', () => {
    console.log('\nRecibido SIGINT. Limpiando...');
    closeBrowser().then(() => process.exit(0));
});

// Ejecutar
main().catch(error => {
    console.error('Error fatal:', error);
    closeBrowser().then(() => process.exit(1));
});