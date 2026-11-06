import { spawn } from "node:child_process";
import { once } from "node:events";

const chromeBin = process.env.CHROME || "/usr/bin/google-chrome-stable";
const port = 8877;
const debugPort = 9333;
const root = new URL("..", import.meta.url);

const server = spawn("python3", ["-m", "http.server", String(port)], {
  cwd: root.pathname,
  stdio: "ignore",
});
const chrome = spawn(
  chromeBin,
  [
    "--headless=new",
    "--disable-gpu",
    "--no-sandbox",
    `--remote-debugging-port=${debugPort}`,
    "--user-data-dir=/tmp/anistar-cdp-a9b9",
    "--allow-insecure-localhost",
    "about:blank",
  ],
  { stdio: "ignore" }
);

const failures = [];
let ws;
let messageId = 0;
const pending = new Map();
const waiters = [];

function fail(message) {
  failures.push(message);
}

function send(method, params = {}) {
  const id = ++messageId;
  ws.send(JSON.stringify({ id, method, params }));
  return new Promise((resolve, reject) => pending.set(id, { resolve, reject }));
}

function onMessage(event) {
  const message = JSON.parse(event.data);
  if (message.id && pending.has(message.id)) {
    const { resolve, reject } = pending.get(message.id);
    pending.delete(message.id);
    if (message.error) reject(new Error(JSON.stringify(message.error)));
    else resolve(message.result);
    return;
  }
  waiters.forEach((waiter) => waiter(message));
}

function waitFor(method) {
  return new Promise((resolve) => {
    const waiter = (message) => {
      if (message.method === method) {
        waiters.splice(waiters.indexOf(waiter), 1);
        resolve(message.params);
      }
    };
    waiters.push(waiter);
  });
}

async function evaluate(expression) {
  const result = await send("Runtime.evaluate", {
    expression,
    returnByValue: true,
    awaitPromise: true,
  });
  if (result.exceptionDetails) {
    throw new Error(JSON.stringify(result.exceptionDetails));
  }
  return result.result.value;
}

async function openPage(path) {
  const loaded = waitFor("Page.loadEventFired");
  await send("Page.navigate", { url: `http://127.0.0.1:${port}${path}` });
  await loaded;
  await evaluate("document.fonts.ready");
}

async function setViewport(width, height) {
  await send("Emulation.setDeviceMetricsOverride", {
    width,
    height,
    deviceScaleFactor: 1,
    mobile: width < 700,
  });
}

async function assertLogo(label, minWidth) {
  const logo = await evaluate(`(() => {
    const img = document.querySelector("header .brand img");
    return img.decode().then(() => {
      const rect = img.getBoundingClientRect();
      return {
        alt: img.alt,
        w: rect.width,
        h: rect.height,
        nw: img.naturalWidth,
        nh: img.naturalHeight,
        complete: img.complete,
      };
    });
  })()`);
  if (logo.alt !== "Anistar" || !logo.complete || logo.nw !== 1275 || logo.nh !== 859) {
    fail(`${label} is not the lockup: ${JSON.stringify(logo)}`);
  }
  if (logo.w < minWidth || logo.h < 80) fail(`${label} is too small: ${JSON.stringify(logo)}`);
  const shown = logo.w / logo.h;
  const intrinsic = logo.nw / logo.nh;
  if (Math.abs(shown - intrinsic) > 0.03) fail(`${label} is distorted: ${JSON.stringify(logo)}`);
}

async function assertNoOverflow(label) {
  const widths = await evaluate("[document.documentElement.scrollWidth, document.documentElement.clientWidth]");
  if (widths[0] > widths[1] + 1) fail(`${label} overflows: ${widths.join(" > ")}`);
}

async function connect() {
  let version;
  for (let attempt = 0; attempt < 40; attempt += 1) {
    try {
      version = await fetch(`http://127.0.0.1:${debugPort}/json/version`).then((response) => response.json());
      break;
    } catch {
      await new Promise((resolve) => setTimeout(resolve, 150));
    }
  }
  if (!version) throw new Error("Chrome debugging port did not open");
  const created = await fetch(`http://127.0.0.1:${debugPort}/json/new?about:blank`, { method: "PUT" }).then((response) =>
    response.json()
  );
  ws = new WebSocket(created.webSocketDebuggerUrl);
  ws.addEventListener("message", onMessage);
  await once(ws, "open");
  await send("Page.enable");
  await send("Runtime.enable");
  await send("Network.enable");
}

const requests = [];
function trackRequests() {
  waiters.push((message) => {
    if (message.method === "Network.requestWillBeSent") requests.push(message.params.request);
  });
}

try {
  await connect();
  trackRequests();
  await setViewport(1440, 900);
  await openPage("/");
  const home = await evaluate(`(() => {
    const nav = document.querySelector("#primary-nav");
    const style = getComputedStyle(nav);
    return {
      status: document.body.innerText.includes("Anistar is a new agency. This website is under construction, and representation and booking are not yet available."),
      explore: !!document.querySelector('a[href="/talent/"]'),
      interest: !!document.querySelector('a[href="/apply/"]'),
      planning: !!document.querySelector('a[href="/book/"]'),
      bookCta: document.body.innerText.includes("Book talent"),
      navDisplay: style.display,
      license: document.body.dataset.licenseStatus,
      email: document.body.dataset.inquiryEmail || "",
    };
  })()`);
  if (!home.status) fail("home is missing the development status");
  if (!home.explore || !home.interest || !home.planning) fail("home is missing a public path");
  if (home.bookCta) fail("home still shows Book talent");
  if (home.navDisplay === "none") fail("primary navigation is hidden at 1440");
  if (home.license !== "forming" || home.email) fail("license or email dataset is wrong");
  await assertLogo("header logo 1440", 200);
  await assertNoOverflow("home 1440");

  await setViewport(390, 844);
  await openPage("/");
  const mobileNav = await evaluate(`getComputedStyle(document.querySelector("#primary-nav")).display`);
  if (mobileNav === "none") fail("primary navigation is hidden at 390");
  const cta = await evaluate(`(() => {
    const link = document.querySelector('a.btn[href="/apply/"]');
    const rect = link.getBoundingClientRect();
    return { top: rect.top, height: rect.height, text: link.textContent };
  })()`);
  if (cta.text !== "Talent application" || cta.height < 44 || cta.top > 844) {
    fail(`primary CTA is not visible on the first mobile screen: ${JSON.stringify(cta)}`);
  }
  await assertLogo("header logo 390", 200);
  await assertNoOverflow("home 390");

  await send("Input.dispatchKeyEvent", {
    type: "keyDown",
    key: "Tab",
    code: "Tab",
    windowsVirtualKeyCode: 9,
    nativeVirtualKeyCode: 9,
  });
  await send("Input.dispatchKeyEvent", {
    type: "keyUp",
    key: "Tab",
    code: "Tab",
    windowsVirtualKeyCode: 9,
    nativeVirtualKeyCode: 9,
  });
  const focus = await evaluate(`(() => {
    const el = document.activeElement;
    const style = getComputedStyle(el);
    return { text: (el.textContent || "").trim().slice(0, 40), outline: style.outlineColor, style: style.outlineStyle };
  })()`);
  if (!/Skip to content/.test(focus.text)) fail(`first tab did not reach the skip link: ${JSON.stringify(focus)}`);
  if (focus.style === "none" || !focus.outline.includes("27, 23, 77")) {
    fail(`skip link focus ring is not navy: ${JSON.stringify(focus)}`);
  }

  await setViewport(1440, 900);
  await openPage("/talent/cosplay-fashion/");
  await assertNoOverflow("division 1440");
  await setViewport(390, 844);
  await openPage("/talent/cosplay-fashion/");
  await assertNoOverflow("division 390");
  await evaluate(`document.querySelector('.brief-add[data-brief="Guest Cosplayers"]').click()`);
  const stored = await evaluate(`localStorage.getItem("anistar-brief")`);
  if (!stored.includes("Guest Cosplayers")) fail(`shortlist was not stored: ${stored}`);
  const pressed = await evaluate(`document.querySelector('.brief-add[data-brief="Guest Cosplayers"]').getAttribute("aria-pressed")`);
  if (pressed !== "true") fail("shortlist button did not toggle");

  requests.length = 0;
  await openPage("/book/?division=Cosplay%20%26%20Fashion");
  await setViewport(390, 844);
  await assertNoOverflow("planning 390");
  await setViewport(1440, 900);
  await assertNoOverflow("planning 1440");
  const planning = await evaluate(`(() => {
    document.querySelector("[name=org]").value = "North Station";
    document.querySelector("[name=type]").value = "Brand project";
    document.querySelector("[name=details]").value = "A later booth might need a guest cosplayer category.";
    document.querySelector("[data-prepare]").click();
    const note = document.querySelector("[data-result-text]").value;
    const message = document.querySelector("[data-result-msg]").textContent;
    return {
      note,
      message,
      division: document.querySelector("[name=division]").value,
      listed: document.querySelector("[data-brief-list]").textContent,
    };
  })()`);
  if (planning.division !== "Cosplay & Fashion") fail("planning division was not prefilled");
  if (!planning.listed.includes("Guest Cosplayers")) fail("planning page missed the shortlist");
  if (!planning.note.includes("ANISTAR PLANNING NOTE") || !planning.note.includes("Guest Cosplayers")) {
    fail(`planning note is incomplete: ${planning.note}`);
  }
  if (!planning.note.includes("Nothing was sent. This is not a booking.")) fail("planning note is missing the no-send line");
  if (planning.message !== "Nothing was sent. Anistar did not receive this note. Copy it if you want to keep it.") {
    fail(`planning message changed: ${planning.message}`);
  }
  const badPlanRequests = requests.filter((request) => request.method !== "GET" || request.url.startsWith("mailto:"));
  if (badPlanRequests.length) fail(`planning page sent a request: ${JSON.stringify(badPlanRequests)}`);

  requests.length = 0;
  await openPage("/apply/?division=Creators%20%26%20Artists");
  await setViewport(390, 844);
  await assertNoOverflow("talent form 390");
  await setViewport(1440, 900);
  await assertNoOverflow("talent form 1440");
  const talent = await evaluate(`(() => {
    const form = document.querySelector("#apply-form");
    const prefilled = form.querySelector("[name=division]").value;
    form.querySelector("[data-prepare]").click();
    const emptyError = form.querySelector(".form-error").textContent;
    const resultHidden = form.querySelector("[data-result]").hidden;
    form.querySelector("[name=name]").value = "A Public Name";
    form.querySelector("[name=email]").value = "artist@example.com";
    const division = form.querySelector("[name=division]");
    division.value = "Creators & Artists";
    division.dispatchEvent(new Event("change", { bubbles: true }));
    form.querySelector("[name=specialty]").value = "Manga Artists (Mangaka)";
    form.querySelector("[name=url]").value = "https://example.com/portfolio";
    form.querySelector("[name=languages]").value = "English, Japanese";
    form.querySelector("[name=goals]").value = "Convention panels and a category page.";
    form.querySelector("[name=adult]").checked = true;
    form.querySelector("[data-prepare]").click();
    return {
      prefilled,
      emptyError,
      resultHidden,
      note: form.querySelector("[data-result-text]").value,
      message: form.querySelector("[data-result-msg]").textContent,
      copyLabel: form.querySelector("[data-copy]").textContent,
      stored: localStorage.getItem("anistar-brief"),
    };
  })()`);
  if (talent.prefilled !== "Creators & Artists") fail(`division was not prefilled: ${talent.prefilled}`);
  if (talent.resultHidden !== true || !talent.emptyError) fail(`empty application did not stay unsent: ${JSON.stringify(talent)}`);
  if (!talent.note.includes("ANISTAR TALENT APPLICATION")) fail("talent note has the wrong heading");
  if (talent.note.includes("Guest Cosplayers") || talent.note.includes("PLANNING NOTE")) {
    fail(`talent note mixed in the client shortlist: ${talent.note}`);
  }
  if (!talent.note.includes("https://example.com/portfolio") || !talent.note.includes("18 or older: yes") || !talent.note.includes("artist@example.com")) {
    fail(`talent note dropped public fields: ${talent.note}`);
  }
  if (!talent.note.includes("Nothing was sent. This is not a representation agreement.")) {
    fail("talent note is missing the no-send line");
  }
  if (talent.message !== "Nothing was sent. Anistar did not receive this application. Copy it if you want to keep it.") {
    fail(`talent message changed: ${talent.message}`);
  }
  if (talent.copyLabel !== "Copy application") fail(`copy control changed: ${talent.copyLabel}`);
  if (!talent.stored || talent.stored.includes("A Public Name") || talent.stored.includes("example.com") || talent.stored.includes("artist@")) {
    fail(`form details were stored: ${talent.stored}`);
  }
  const badTalentRequests = requests.filter((request) => request.method !== "GET" || request.url.startsWith("mailto:"));
  if (badTalentRequests.length) fail(`talent form sent a request: ${JSON.stringify(badTalentRequests)}`);
} catch (error) {
  fail(error.stack || String(error));
} finally {
  try { ws && ws.close(); } catch {}
  chrome.kill("SIGKILL");
  server.kill("SIGKILL");
}

if (failures.length) {
  console.error(failures.join("\n\n"));
  process.exit(1);
}
console.log("browser flows ok");
