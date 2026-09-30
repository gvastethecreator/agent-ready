// agent-ready-site: read-only snapshot of the rendered page as a browser agent meets it.
// Evaluate the whole file as one expression in the page (DevTools, Playwright, or a browser tool's
// JavaScript runner). Returns bounded JSON. Accessible names are approximations of the
// accessibility tree; confirm doubtful cases in the tree itself.
(() => {
  const LIMIT = 6;
  const clean = (s) => (s || "").replace(/\s+/g, " ").trim();
  const snippet = (el) => el.outerHTML.slice(0, 140);
  const shown = (el) => {
    const r = el.getBoundingClientRect();
    const cs = getComputedStyle(el);
    return r.width > 0 && r.height > 0 && cs.visibility !== "hidden" && cs.display !== "none";
  };
  const isField = (el) => /^(INPUT|SELECT|TEXTAREA)$/.test(el.tagName);

  function accName(el) {
    const aria = clean(el.getAttribute("aria-label"));
    if (aria) return aria;
    const ids = (el.getAttribute("aria-labelledby") || "").split(/\s+/).filter(Boolean);
    const byRef = clean(ids.map((id) => document.getElementById(id)?.textContent || "").join(" "));
    if (byRef) return byRef;
    if (el.labels && el.labels.length) {
      const label = clean([...el.labels].map((l) => l.textContent).join(" "));
      if (label) return label;
    }
    if (el.tagName === "INPUT" && /^(submit|button|reset)$/i.test(el.type)) return clean(el.value);
    if (!isField(el)) {
      const own = clean(el.innerText || el.textContent);
      if (own) return own;
      const alt = clean([...el.querySelectorAll("img[alt]")].map((i) => i.alt).join(" "));
      if (alt) return alt;
      const svgTitle = clean(el.querySelector("svg title")?.textContent);
      if (svgTitle) return svgTitle;
    }
    return clean(el.getAttribute("title"));
  }

  const interactiveSelector = [
    "a[href]", "button", "input:not([type=hidden])", "select", "textarea", "summary",
    "[role=button]", "[role=link]", "[role=checkbox]", "[role=radio]", "[role=switch]", "[role=tab]",
    "[role=menuitem]", "[role=combobox]", "[role=option]", "[role=slider]", "[contenteditable=true]",
    "[tabindex]:not([tabindex='-1'])",
  ].join(",");
  const interactive = [...document.querySelectorAll(interactiveSelector)].filter(shown);

  const unnamed = interactive.filter((el) => !accName(el));
  const fields = interactive.filter((el) => isField(el) && !/^(submit|button|reset|image)$/i.test(el.type || ""));
  const unlabeledFields = fields.filter((el) => !accName(el));

  const nameCounts = {};
  for (const el of interactive.filter((e) => /^(A|BUTTON)$/.test(e.tagName) || e.getAttribute("role") === "button")) {
    const name = accName(el).toLowerCase();
    if (name && name.length <= 30) nameCounts[name] = (nameCounts[name] || 0) + 1;
  }
  const ambiguousNames = Object.entries(nameCounts)
    .filter(([, n]) => n > 1)
    .sort((a, b) => b[1] - a[1])
    .slice(0, LIMIT)
    .map(([name, count]) => ({ name, count }));

  // Pointer-styled elements that are not reachable as controls.
  const clickableNonSemantic = [];
  for (const el of [...document.querySelectorAll("div, span, li, td, img, p, svg")].slice(0, 4000)) {
    if (clickableNonSemantic.length >= 50) break;
    if (el.closest(interactiveSelector) || el.querySelector(interactiveSelector)) continue;
    if (clickableNonSemantic.some((parent) => parent.contains(el))) continue;
    if (getComputedStyle(el).cursor === "pointer" && shown(el)) clickableNonSemantic.push(el);
  }

  const dialogs = [...document.querySelectorAll("[role=dialog], [role=alertdialog], [aria-modal=true], dialog[open]")]
    .filter(shown)
    .map((el) => ({
      name: accName(el).slice(0, 80),
      consent_like: /cookie|consent|privacy|gdpr/i.test(el.innerText || ""),
      closable: [...el.querySelectorAll("button, [role=button]")].some((b) => accName(b)),
    }));

  const frames = [...document.querySelectorAll("iframe")].filter(shown);
  const crossOriginFrames = frames.filter((f) => {
    try { return new URL(f.src, location.href).origin !== location.origin; } catch { return false; }
  });

  const modelContext = document.modelContext || navigator.modelContext;
  return {
    url: location.href,
    title: document.title,
    rendered_text_chars: clean(document.body?.innerText).length,
    landmarks: {
      main: document.querySelectorAll("main, [role=main]").length,
      nav: document.querySelectorAll("nav, [role=navigation]").length,
      h1: document.querySelectorAll("h1").length,
    },
    interactive: interactive.length,
    unnamed: unnamed.length,
    unnamed_examples: unnamed.slice(0, LIMIT).map(snippet),
    ambiguous_names: ambiguousNames,
    fields: fields.length,
    unlabeled_fields: unlabeledFields.length,
    placeholder_only_fields: unlabeledFields.filter((el) => el.placeholder).length,
    unlabeled_field_examples: unlabeledFields.slice(0, LIMIT).map(snippet),
    fields_without_autocomplete: fields.filter((el) => el.tagName === "INPUT" && !el.autocomplete
      && /^(email|tel|text)$/i.test(el.type) && /name|mail|phone|tel|address|zip|postal|city|country/i.test(`${el.name} ${el.id}`)).length,
    clickable_non_semantic: clickableNonSemantic.length,
    clickable_non_semantic_examples: clickableNonSemantic.slice(0, LIMIT).map(snippet),
    images_missing_alt: [...document.images].filter((i) => shown(i) && !i.hasAttribute("alt")).length,
    canvas_large: [...document.querySelectorAll("canvas")].filter((c) => shown(c) && c.width * c.height > 40000).length,
    iframes: frames.length,
    cross_origin_iframes: crossOriginFrames.length,
    open_dialogs: dialogs,
    live_regions: document.querySelectorAll("[aria-live], [role=status], [role=alert]").length,
    webmcp: {
      model_context: Boolean(modelContext),
      register_tool: typeof modelContext?.registerTool === "function",
      declarative_forms: document.querySelectorAll("form[toolname]").length,
    },
  };
})();
