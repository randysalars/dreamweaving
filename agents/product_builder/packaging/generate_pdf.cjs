
const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

async function generatePDF() {
  const browser = await puppeteer.launch({
    headless: "new",
    args: ['--no-sandbox', '--disable-setuid-sandbox'] 
  });
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

  await page.setContent(styledContent, { waitUntil: 'networkidle0' });

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
