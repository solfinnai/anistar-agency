const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];
const EMAIL = document.body.dataset.inquiryEmail || "";
const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

const menuButton = $(".menu-btn");
const navigation = $("#primary-nav");
function setMenu(open) {
  if (!menuButton || !navigation) return;
  menuButton.setAttribute("aria-expanded", String(open));
  menuButton.textContent = open ? "Close" : "Menu";
  navigation.classList.toggle("open", open);
}
menuButton?.addEventListener("click", () => {
  setMenu(menuButton.getAttribute("aria-expanded") !== "true");
});
$$("#primary-nav a").forEach((a) => a.addEventListener("click", () => setMenu(false)));
document.addEventListener("keydown", (ev) => {
  if (ev.key === "Escape") setMenu(false);
});

const search = $("#q");
const finder = $("#finder");
function applySearch() {
  if (!search) return;
  const term = search.value.trim().toLowerCase();
  let n = 0;
  $$(".field").forEach((field) => {
    const blob = field.dataset.search || "";
    let vis = 0;
    $$("li", field).forEach((li) => {
      const ok = !term || (li.dataset.search || "").includes(term) || blob.includes(term);
      li.hidden = !ok;
      if (ok) vis += 1;
    });
    field.hidden = vis === 0;
    n += vis;
  });
  const count = $("#count");
  const none = $("#none");
  const clear = $("#clear");
  if (count) count.textContent = term ? `${n} ${n === 1 ? "match" : "matches"}` : "";
  if (none) none.hidden = !term || n > 0;
  if (clear) clear.hidden = !term;
}
if (search) {
  search.addEventListener("input", applySearch);
  finder?.addEventListener("submit", (ev) => {
    ev.preventDefault();
    const url = new URL(location.href);
    const v = search.value.trim();
    if (v) url.searchParams.set("q", v);
    else url.searchParams.delete("q");
    history.replaceState(null, "", url);
    applySearch();
  });
  $("#clear")?.addEventListener("click", () => {
    search.value = "";
    const url = new URL(location.href);
    url.searchParams.delete("q");
    history.replaceState(null, "", url);
    applySearch();
    search.focus();
  });
  const params = new URLSearchParams(location.search);
  if (params.get("q")) {
    search.value = params.get("q");
    applySearch();
  }
}

const divisionSelect = $("[name=division]");
if (divisionSelect) {
  const wanted = new URLSearchParams(location.search).get("division");
  if (wanted && [...divisionSelect.options].some((o) => o.value === wanted)) divisionSelect.value = wanted;
}

function handle(form, title, build) {
  form.addEventListener("submit", (ev) => {
    ev.preventDefault();
    const err = $(".form-error", form);
    const bad = $$("[required]", form).filter((i) => {
      if (!i.value.trim()) return true;
      if (i.type === "email" && !/^\S+@\S+\.\S+$/.test(i.value)) return true;
      return false;
    });
    $$("[aria-invalid]", form).forEach((i) => i.removeAttribute("aria-invalid"));
    bad.forEach((i) => i.setAttribute("aria-invalid", "true"));
    if (bad.length) {
      const emailBad = bad.find((i) => i.type === "email" && i.value.trim());
      err.hidden = false;
      err.textContent = emailBad
        ? "Enter an email address that looks complete."
        : `Please fill in ${bad.map((i) => i.dataset.label || "a field").join(", ")}.`;
      bad[0].focus();
      return;
    }
    err.hidden = true;
    const f = Object.fromEntries(new FormData(form));
    const text = build(f);
    const res = $("[data-result]", form);
    const msg = $("[data-result-msg]", form);
    res.hidden = false;
    $("[data-result-text]", form).value = text;
    if (EMAIL) {
      msg.textContent = "Your email app should open with this note. If it does not, copy the text below.";
      location.href = `mailto:${EMAIL}?subject=${encodeURIComponent(title + ": " + (f.org || f.name))}&body=${encodeURIComponent(text)}`;
    } else {
      msg.textContent = "Nothing was sent. Anistar has no public inbox on this site yet. Copy this note and keep it.";
    }
    msg.focus();
    res.scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "nearest" });
  });
}

const line = (label, value) => `${label}: ${value && String(value).trim() ? value : "-"}`;
const inq = $("#inquiry-form");
if (inq) {
  handle(inq, "Anistar booking", (f) =>
    [
      "ANISTAR BOOKING NOTE",
      line("Name", f.name),
      line("Email", f.email),
      line("Organization", f.org),
      line("Project type", f.type),
      line("Field", f.division),
      line("Specialty", f.specialty),
      line("Timing", f.timing),
      line("Budget", f.budget),
      "",
      "The job:",
      f.details || "-",
    ].join("\n")
  );
}
const ap = $("#apply-form");
if (ap) {
  handle(ap, "Anistar application", (f) =>
    [
      "ANISTAR REPRESENTATION NOTE",
      line("Name", f.name),
      line("Email", f.email),
      line("Field", f.specialty),
      "",
      "Links:",
      f.links || "-",
      "",
      "About the work:",
      f.about || "-",
    ].join("\n")
  );
}

$$("[data-copy]").forEach((b) =>
  b.addEventListener("click", async () => {
    const t = $("[data-result-text]", b.closest("form"));
    try {
      await navigator.clipboard.writeText(t.value);
      b.textContent = "Copied";
    } catch {
      t.focus();
      t.select();
      b.textContent = "Select the note and copy it";
    }
  })
);
