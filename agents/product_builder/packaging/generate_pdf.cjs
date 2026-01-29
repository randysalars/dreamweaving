
const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');
const { execSync } = require('child_process');

/**
 * Find Chrome/Chromium executable on the system
 */
function findSystemChrome() {
  const candidates = [
    '/usr/bin/google-chrome',
    '/usr/bin/google-chrome-stable',
    '/usr/bin/chromium-browser',
    '/usr/bin/chromium',
    '/snap/bin/chromium',
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  ];
  
  for (const candidate of candidates) {
    if (fs.existsSync(candidate)) {
      console.log(`Found system Chrome at: ${candidate}`);
      return candidate;
    }
  }
  
  // Try 'which' command as fallback
  try {
    const result = execSync('which google-chrome chromium-browser chromium 2>/dev/null | head -1', { encoding: 'utf8' }).trim();
    if (result && fs.existsSync(result)) {
      console.log(`Found Chrome via 'which': ${result}`);
      return result;
    }
  } catch (e) {
    // Ignore errors from which command
  }
  
  return null;
}

async function generatePDF() {
  const systemChrome = findSystemChrome();
  
  const launchOptions = {
    headless: "new",
    args: [
        '--no-sandbox', 
        '--disable-setuid-sandbox', 
        '--allow-file-access-from-files',
        '--enable-local-file-accesses',
        '--disable-gpu',
        '--disable-dev-shm-usage'
    ] 
  };
  
  // Use system Chrome if Puppeteer's bundled Chrome isn't available
  if (systemChrome) {
    launchOptions.executablePath = systemChrome;
  }
  
  let browser;
  try {
    browser = await puppeteer.launch(launchOptions);
  } catch (err) {
    console.error(`Failed to launch browser: ${err.message}`);
    // If system Chrome path was provided but failed, try without it
    if (systemChrome && !launchOptions.executablePath) {
      throw err;
    }
    // Rethrow to trigger Python fallback
    throw err;
  }
  const page = await browser.newPage();
  
  // Arguments: node generate_pdf.cjs <input_html> <output_pdf>
  const args = process.argv.slice(2);
  if (args.length < 2) {
      console.error("Usage: node generate_pdf.cjs <input_html> <output_pdf>");
      process.exit(1);
  }

  const htmlPath = path.resolve(args[0]);
  const pdfPath = path.resolve(args[1]);

  if (!fs.existsSync(htmlPath)) {
      console.error(`HTML source not found at ${htmlPath}`);
      await browser.close();
      process.exit(1);
  }

  const content = fs.readFileSync(htmlPath, 'utf8');
  
  // Improve styling clearly for PDF
  const styledContent = `
  <html>
  <head>
      <style>
          body { font-family: "Inter", system-ui, sans-serif; padding: 40px; line-height: 1.6; color: #333; }
          h1 { color: #1a202c; border-bottom: 2px solid #edf2f7; padding-bottom: 10px; margin-top: 40px; }
          h2 { color: #2d3748; margin-top: 30px; }
          blockquote { border-left: 4px solid #4299e1; padding-left: 15px; color: #4a5568; background: #ebf8ff; padding: 10px; border-radius: 4px; margin: 20px 0; }
          pre { background: #f7fafc; padding: 15px; border-radius: 5px; overflow-x: auto; font-family: monospace; border: 1px solid #e2e8f0; }
          ul, ol { margin-bottom: 15px; padding-left: 20px; }
          li { margin-bottom: 8px; }
          .cover { text-align: center; page-break-after: always; padding-top: 200px; }
          .cover h1 { border: none; font-size: 48px; margin-bottom: 20px; }
          .cover p { font-size: 24px; color: #718096; }
          .toc { page-break-after: always; }
          .chapter { page-break-before: always; }
          img { max-width: 100%; height: auto; border-radius: 8px; margin: 20px 0; }
      </style>
  </head>
  <body>
      ${content}
  </body>
  </html>
  `;

  // Write the styled content back to a temp file so we can load it with file:// protocol
  // This ensures relative paths (images/) are resolved correctly relative to the file.
  const finalHtmlPath = htmlPath.replace('.temp.html', '.final.html');
  fs.writeFileSync(finalHtmlPath, styledContent);
  
  await page.goto('file://' + finalHtmlPath, { waitUntil: 'networkidle0' });

  await page.pdf({
    path: pdfPath,
    format: 'A4',
    printBackground: true,
    margin: {
        top: '20mm',
        right: '20mm',
        bottom: '20mm',
        left: '20mm'
    }
  });

  console.log(`PDF generated successfully at: ${pdfPath}`);

  await browser.close();
}

generatePDF().catch(err => {
    console.error(err);
    process.exit(1);
});
