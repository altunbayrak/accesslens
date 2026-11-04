import { chromium } from "playwright";
import AxeBuilder from "@axe-core/playwright";
const [url, domainsJson = "[]"] = process.argv.slice(2);
const domains = JSON.parse(domainsJson);
function authorized(value) { const u = new URL(value); const h = u.hostname.toLowerCase(); return ["http:","https:"].includes(u.protocol) && domains.some(d => h === d || h.endsWith(`.${d}`)); }
if (!url || !authorized(url)) throw new Error("Worker target is not an authorized HTTP(S) domain");
const browser = await chromium.launch({headless:true,args:["--disable-dev-shm-usage","--no-sandbox"]});
const page = await browser.newPage({viewport:{width:1440,height:900}});
await page.route("**/*", route => authorized(route.request().url()) ? route.continue() : route.abort("blockedbyclient"));
await page.goto(url,{waitUntil:"networkidle",timeout:25000});
const axe = await new AxeBuilder({page}).withTags(["wcag2a","wcag2aa","wcag21aa","wcag22aa"]).analyze();
const screenshot = await page.screenshot({fullPage:true,type:"png"}); await browser.close();
const findings = axe.violations.flatMap(v => v.nodes.map(n => ({category:"accessibility",severity:v.impact||"medium",title:v.help,detail:v.description,remediation:v.helpUrl,url,selector:n.target.join(", "),evidence:{id:v.id,html:n.html,failureSummary:n.failureSummary}})));
process.stdout.write(JSON.stringify({url,findings,screenshotBase64:screenshot.toString("base64"),performance:{engine:"lighthouse",status:"configured-worker"}}));
