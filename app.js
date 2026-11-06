const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];

// Category names only. Form fields are never written here, and nothing is sent.
const KEY = "anistar-brief";

const getB = () => {
  try {
    const value = JSON.parse(localStorage.getItem(KEY));
    return Array.isArray(value) ? value.filter((item) => typeof item === "string") : [];
  } catch {
    return [];
  }
};

const setB = (items) => {
  try {
    localStorage.setItem(KEY, JSON.stringify(items));
  } catch {
    /* private mode and blocked storage still leave the note on the page */
  }
  render();
};

function toggle(name) {
  const items = getB();
  setB(items.includes(name) ? items.filter((item) => item !== name) : [...items, name]);
}

function render() {
  const items = getB();
  $$(".brief-add").forEach((button) => {
    const on = items.includes(button.dataset.brief);
    button.setAttribute("aria-pressed", String(on));
    button.textContent = on ? "Added" : "Add";
    const verb = on ? "Remove " : "Add ";
    const tail = on ? " from the planning note" : " to the planning note";
    button.setAttribute("aria-label", verb + button.dataset.brief + tail);
  });
  $$("[data-brief-count]").forEach((node) => {
    node.hidden = items.length === 0;
    node.textContent = items.length ? String(items.length) : "";
  });
  const list = $("[data-brief-list]");
  if (list) {
    list.replaceChildren();
    items.forEach((name) => {
      const li = document.createElement("li");
      const label = document.createElement("span");
      label.textContent = name;
      const remove = document.createElement("button");
      remove.type = "button";
      remove.className = "textbtn";
      remove.textContent = "Remove";
      remove.setAttribute("aria-label", "Remove " + name + " from the planning note");
      remove.addEventListener("click", () => toggle(name));
      li.append(label, remove);
      list.append(li);
    });
    const empty = $("[data-brief-empty]");
    if (empty) empty.hidden = items.length > 0;
  }
}

document.addEventListener("click", (ev) => {
  const button = ev.target.closest(".brief-add");
  if (button) toggle(button.dataset.brief);
});

$("[data-brief-picker]")?.addEventListener("change", (ev) => {
  const value = ev.target.value;
  if (value && !getB().includes(value)) toggle(value);
  ev.target.value = "";
});

const search = $("#q");
const finder = $("#finder");
let division = "all";

function setDivision(next) {
  division = next || "all";
  $$(".filter").forEach((button) => {
    button.setAttribute("aria-pressed", String(button.dataset.division === division));
  });
}

function applySearch() {
  if (!search) return;
  const term = search.value.trim().toLowerCase();
  let count = 0;
  $$(".field").forEach((field) => {
    const inDivision = division === "all" || field.dataset.division === division;
    const blob = field.dataset.search || "";
    let visible = 0;
    $$("li", field).forEach((li) => {
      const matches = !term || (li.dataset.search || "").includes(term) || blob.includes(term);
      const ok = inDivision && matches;
      li.hidden = !ok;
      if (ok) visible += 1;
    });
    field.hidden = !inDivision || visible === 0;
    count += field.hidden ? 0 : visible;
  });
  const countNode = $("#count");
  const none = $("#none");
  const clear = $("#clear");
  if (countNode) {
    countNode.textContent = term || division !== "all" ? `${count} ${count === 1 ? "match" : "matches"}` : "";
  }
  if (none) none.hidden = (!term && division === "all") || count > 0;
  if (clear) clear.hidden = !term && division === "all";
}

function writeFinderUrl() {
  const url = new URL(location.href);
  const value = search.value.trim();
  if (value) url.searchParams.set("q", value);
  else url.searchParams.delete("q");
  if (division !== "all") url.searchParams.set("division", division);
  else url.searchParams.delete("division");
  history.replaceState(null, "", url);
}

if (search) {
  search.addEventListener("input", () => {
    applySearch();
    writeFinderUrl();
  });
  finder?.addEventListener("submit", (ev) => {
    ev.preventDefault();
    applySearch();
    writeFinderUrl();
  });
  $$(".filter").forEach((button) => {
    button.addEventListener("click", () => {
      setDivision(button.dataset.division);
      applySearch();
      writeFinderUrl();
      button.focus();
    });
  });
  $("#clear")?.addEventListener("click", () => {
    search.value = "";
    setDivision("all");
    applySearch();
    writeFinderUrl();
    search.focus();
  });
  const params = new URLSearchParams(location.search);
  if (params.get("division")) setDivision(params.get("division"));
  if (params.get("q")) search.value = params.get("q");
  applySearch();
}

function syncSpecialty(form) {
  const divisionSelect = $("[name=division]", form);
  const specialty = $("[name=specialty]", form);
  if (!divisionSelect || !specialty) return;
  const wanted = divisionSelect.value;
  $$("optgroup", specialty).forEach((group) => {
    const on = !wanted || group.label === wanted;
    $$("option", group).forEach((option) => {
      option.disabled = !on;
    });
  });
  const selected = specialty.selectedOptions[0];
  if (selected && selected.disabled) specialty.value = "";
}

function prefill(form) {
  const params = new URLSearchParams(location.search);
  const divisionSelect = $("[name=division]", form);
  const specialty = $("[name=specialty]", form);
  const wantedDivision = params.get("division");
  const wantedSpecialty = params.get("specialty");
  if (divisionSelect && wantedDivision && [...divisionSelect.options].some((option) => option.value === wantedDivision)) {
    divisionSelect.value = wantedDivision;
  }
  syncSpecialty(form);
  if (specialty && wantedSpecialty && [...specialty.options].some((option) => option.value === wantedSpecialty && !option.disabled)) {
    specialty.value = wantedSpecialty;
  }
}

function invalid(field) {
  if (field.type === "checkbox") return !field.checked;
  const value = String(field.value || "").trim();
  if (!value) return true;
  if (field.type === "url") {
    try {
      const url = new URL(value);
      if (url.protocol !== "http:" && url.protocol !== "https:") return true;
    } catch {
      return true;
    }
  }
  return false;
}

const line = (label, value) => `${label}: ${value && String(value).trim() ? String(value).trim() : "-"}`;

const NO_SEND = "Nothing was sent. Anistar did not receive this note. Copy it if you want to keep it.";

function handle(form, build) {
  const prepare = () => {
    const error = $(".form-error", form);
    const fields = $$("input, select, textarea", form).filter((field) => field.required || field.type === "url");
    const bad = fields.filter(invalid);
    $$("[aria-invalid]", form).forEach((field) => field.removeAttribute("aria-invalid"));
    bad.forEach((field) => field.setAttribute("aria-invalid", "true"));
    if (!error.id) error.id = form.id + "-error";
    if (bad.length) {
      const urlBad = bad.find((field) => field.type === "url" && field.value.trim());
      error.hidden = false;
      error.textContent = urlBad
        ? "Enter a public https:// address."
        : `Please fill in ${bad.map((field) => field.dataset.label || "a field").join(", ")}.`;
      bad.forEach((field) => field.setAttribute("aria-describedby", error.id));
      bad[0].focus();
      return;
    }
    error.hidden = true;
    $$("[aria-describedby]", form).forEach((field) => field.removeAttribute("aria-describedby"));
    const data = Object.fromEntries(new FormData(form));
    const result = $("[data-result]", form);
    const message = $("[data-result-msg]", form);
    result.hidden = false;
    $("[data-result-text]", form).value = build(data);
    message.textContent = NO_SEND;
    message.focus();
  };
  form.addEventListener("submit", (ev) => {
    ev.preventDefault();
    prepare();
  });
  $("[data-prepare]", form)?.addEventListener("click", prepare);
  form.addEventListener("keydown", (ev) => {
    if (ev.key === "Enter" && ev.target.matches("input")) {
      ev.preventDefault();
      prepare();
    }
  });
  $("[name=division]", form)?.addEventListener("change", () => syncSpecialty(form));
  prefill(form);
}

const inquiry = $("#inquiry-form");
if (inquiry) {
  handle(inquiry, (data) =>
    [
      "ANISTAR PLANNING NOTE",
      "Nothing was sent. This is not a booking.",
      line("Organization", data.org),
      line("Project type", data.type),
      line("Timing", data.timing),
      line("City", data.city),
      line("Division", data.division),
      line("Category", data.specialty),
      "",
      "Categories in this browser:",
      getB().join("\n") || "-",
      "",
      "What the project would need:",
      data.details || "-",
    ].join("\n")
  );
}

const applyForm = $("#apply-form");
if (applyForm) {
  handle(applyForm, (data) =>
    [
      "ANISTAR TALENT INTEREST NOTE",
      "Nothing was sent. This is not a representation agreement.",
      line("Public name", data.name),
      line("Division", data.division),
      line("Category", data.specialty),
      line("Public URL", data.url),
      line("18 or older", data.adult === "yes" ? "yes" : "no"),
      "",
      "Note:",
      data.about || "-",
    ].join("\n")
  );
}

$$("[data-copy]").forEach((button) => {
  button.addEventListener("click", async () => {
    const note = $("[data-result-text]", button.closest("form"));
    try {
      await navigator.clipboard.writeText(note.value);
      button.textContent = "Copied";
    } catch {
      note.focus();
      note.select();
      button.textContent = "Select the note and copy it";
    }
  });
});

render();
