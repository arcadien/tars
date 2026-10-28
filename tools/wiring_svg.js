// Export the wiring sketch of tars4_wiring.html as a static SVG for the README (light theme, no JavaScript).
// usage: node tools/wiring_svg.js [hardware/tars4_wiring.html] [renders/tars4_wiring.svg]
const fs = require('fs');
const src = process.argv[2] || 'hardware/tars4_wiring.html';
const out = process.argv[3] || 'renders/tars4_wiring.svg';
const html = fs.readFileSync(src, 'utf8');

// light theme tokens from the first :root block
const tokens = {};
for (const m of html.match(/:root \{([^}]*)\}/)[1].matchAll(/--([\w-]+):\s*([^;]+);/g)) tokens[m[1]] = m[2].trim();
const resolve = s => String(s).replace(/var\(--([\w-]+)\)/g, (_, k) => tokens[k] || '#000');

// minimal DOM: just enough for the drawing script
function node(tag) {
  return {
    tag, attrs: {}, children: [], textContent: '',
    setAttribute(k, v) { this.attrs[k] = v; },
    appendChild(c) { this.children.push(c); return c; },
  };
}
const esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/"/g, '&quot;');
function serialize(n) {
  const a = Object.entries(n.attrs).map(([k, v]) => ` ${k}="${esc(resolve(v))}"`).join('');
  const inner = n.children.map(serialize).join('') + esc(n.textContent);
  return `<${n.tag}${a}>${inner}</${n.tag}>`;
}
const svgNode = node('svg');
const document = { getElementById: () => svgNode, createElementNS: (_, tag) => node(tag) };

const script = html.match(/<script>([\s\S]*?)<\/script>/)[1];
new Function('document', script)(document);

const vb = html.match(/viewBox="([^"]+)"/)[1];
const [, , w, h] = vb.split(' ').map(Number);
const style = `.t{font-family:"IBM Plex Mono",Consolas,monospace;fill:${tokens.ink};paint-order:stroke;stroke:${tokens.sheet};stroke-width:.7px;stroke-linejoin:round}`
  + `.t.m{fill:${tokens.muted}}.t.h{font-family:"IBM Plex Sans Condensed","Arial Narrow",sans-serif;font-weight:600}`;
const body = svgNode.children.map(serialize).join('\n');
fs.writeFileSync(out, `<svg xmlns="http://www.w3.org/2000/svg" viewBox="${vb}" width="${w * 7}" height="${h * 7}">\n`
  + `<style>${style}</style>\n<rect x="${vb.split(' ')[0]}" y="${vb.split(' ')[1]}" width="${w}" height="${h}" fill="${tokens.sheet}"/>\n${body}\n</svg>\n`);
console.log(`${out}: ${svgNode.children.length} elements`);
