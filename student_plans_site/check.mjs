// Checks plans.json and the cost math in index.html. Run after every price update:
//   python3 build.py && node check.mjs
// Exits with code 1 and prints what is wrong if anything fails.
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const html = readFileSync(join(here, "index.html"), "utf8");
const data = JSON.parse(readFileSync(join(here, "plans.json"), "utf8"));
const costs = (0, eval)("(" + html.match(/function costs[\s\S]*?\n}\n/)[0] + ")");
const problems = [];
const need = (ok, msg) => { if (!ok) problems.push(msg); };

need(/^\d{4}-\d{2}-\d{2}$/.test(data.checked || ""), "checked must be a YYYY-MM-DD date");
need(Array.isArray(data.plans) && data.plans.length >= 10, "expected at least 10 plans");
need(data.taxes && Object.keys(data.taxes.states || {}).length === 51, "taxes.states must list 50 states and DC");
const seed = html.match(/let DATA = (\{[\s\S]*?\});\n/);
need(seed && JSON.stringify(JSON.parse(seed[1].replace(/<\\\//g, "</"))) === JSON.stringify(data), "index.html is stale: run python3 build.py");

const ids = new Set();
for (const p of data.plans || []) {
  const at = `plan ${p.id}`;
  need(typeof p.id === "string" && !ids.has(p.id), `${at}: id missing or repeated`); ids.add(p.id);
  for (const k of ["carrier", "plan", "network", "data", "link", "source"]) need(typeof p[k] === "string" && p[k], `${at}: ${k} missing`);
  need(typeof p.price === "number" && p.price > 0 && p.price < 300, `${at}: price out of range`);
  need(typeof p.fastGB === "number" && p.fastGB >= 0, `${at}: fastGB missing`);
  for (const k of ["taxesIncluded", "noCreditCheck", "unlimited", "intlWide"]) need(typeof p[k] === "boolean", `${at}: ${k} must be true or false`);
  need(/^https:\/\//.test(p.source || "") && /^https:\/\//.test(p.link || ""), `${at}: link and source must be https URLs`);
  if (p.promo) need(p.promo.price > 0 && p.promo.months >= 1 && typeof p.promo.label === "string", `${at}: promo needs price, months and label`);
  if (p.upfrontMonths) need([1, 3, 6, 12].includes(p.upfrontMonths), `${at}: upfrontMonths must be 3, 6 or 12`);

  for (let lines = 1; lines <= 5; lines++) for (const years of [1, 2, 5, 100]) for (const tax of [0, data.taxes.usAverage, 25.02]) {
    const months = years * 12, c = costs(p, lines, tax, months);
    const ok = c.year1 >= c.advertised - 0.005
      && Math.abs(c.cum[24] - (c.year1 + c.year2)) < 0.01
      && Math.abs(c.cum[12] - c.year1) < 0.01
      && Math.abs(c.advertised + c.rise + c.oneTime + c.taxfees - c.year1) < 0.01
      && c.cum.every((v, i) => i === 0 || v >= c.cum[i - 1] - 1e-9)
      && Number.isFinite(c.cum[months]) && c.monthly > 0;
    if (!ok) { problems.push(`${at}: cost math fails for ${lines} line(s), ${years} year(s), tax ${tax}%`); break; }
  }
}

if (problems.length) { console.error(problems.join("\n")); process.exit(1); }
console.log(`OK: ${data.plans.length} plans, checked ${data.checked}, cost math consistent.`);
