import { chromium } from "file:///C:/Users/user/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/.pnpm/playwright@1.60.0/node_modules/playwright/index.mjs";

const out = "C:/Users/user/Documents/Codex/2026-05-31/files-mentioned-by-the-user-1/outputs/report_assets";
const browser = await chromium.launch({
  headless: true,
  executablePath: "C:/Program Files/Google/Chrome/Application/chrome.exe",
});
const page = await browser.newPage({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 });
const errors = [];
page.on("console", (msg) => {
  if (msg.type() === "error") errors.push(msg.text());
});
page.on("pageerror", (error) => errors.push(error.message));

await page.goto("http://127.0.0.1:8550", { waitUntil: "networkidle" });
await page.waitForTimeout(6000);
await page.screenshot({ path: `${out}/01_dashboard.png`, fullPage: true });

const bodyText = await page.locator("body").innerText().catch(() => "");
console.log(`title=${await page.title()}`);
console.log(`body=${bodyText.slice(0, 1200)}`);

async function openView(label, y, screenshotName) {
  // Flet CanvasKit 화면은 일반 HTML 텍스트 노드를 만들지 않으므로
  // 왼쪽 NavigationRail의 고정 위치를 클릭해 각 화면을 검증한다.
  await page.mouse.click(110, y);
  await page.waitForTimeout(1500);
  await page.screenshot({ path: `${out}/${screenshotName}`, fullPage: true });
  console.log(`captured=${label}`);
}

await openView("볼링공 관리", 166, "02_ball_management.png");
await openView("경기 기록", 210, "03_game_form.png");
await openView("통합 조회", 255, "04_join_result.png");

const mobile = await browser.newPage({ viewport: { width: 412, height: 915 }, deviceScaleFactor: 1 });
await mobile.goto("http://127.0.0.1:8550", { waitUntil: "networkidle" });
await mobile.waitForTimeout(12000);
await mobile.screenshot({ path: `${out}/05_mobile_dashboard.png`, fullPage: true });
await mobile.close();

console.log(`errors=${JSON.stringify(errors)}`);
await browser.close();
