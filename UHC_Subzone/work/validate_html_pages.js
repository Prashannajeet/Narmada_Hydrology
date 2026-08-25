const fs = require("fs");
const path = require("path");

const outputDir = path.join(__dirname, "..", "outputs");
const files = fs.readdirSync(outputDir).filter((file) => file.endsWith(".html"));

for (const file of files) {
  const html = fs.readFileSync(path.join(outputDir, file), "utf8");
  const inlineScripts = [...html.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/g)]
    .map((match) => match[1].trim())
    .filter(Boolean);

  inlineScripts.forEach((script, index) => {
    try {
      new Function(script);
    } catch (error) {
      error.message = `${file} inline script ${index + 1}: ${error.message}`;
      throw error;
    }
  });

  console.log(JSON.stringify({
    file,
    inlineScripts: inlineScripts.length,
    hasNavigation: html.includes('class="site-nav"'),
  }));
}
