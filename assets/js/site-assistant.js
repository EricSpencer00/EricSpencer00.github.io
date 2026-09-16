/* Eric's site assistant: local WebGPU inference, no application backend. */

const MODEL = "Qwen2.5-0.5B-Instruct-q4f16_1-MLC";
const PAGE_LIMIT = 8;
const CONTEXT_LIMIT = 7200;
let engine;
let loading;

function words(value) {
  return (value.toLowerCase().match(/[a-z0-9+.#-]{2,}/g) || [])
    .filter((word) => !new Set(["about", "what", "with", "from", "that", "this", "does", "have", "where", "when", "which", "your", "site"]).has(word));
}

function relevant(question) {
  const terms = words(question);
  const passages = window.ERIC_SITE_KNOWLEDGE?.passages || [];
  return passages
    .map((passage) => {
      const haystack = `${passage.title} ${passage.text}`.toLowerCase();
      const score = terms.reduce((sum, term) => sum + (haystack.includes(term) ? (passage.title.toLowerCase().includes(term) ? 5 : 1) : 0), 0);
      return { ...passage, score };
    })
    .filter((passage) => passage.score > 0)
    .sort((a, b) => b.score - a.score || a.text.length - b.text.length)
    .slice(0, PAGE_LIMIT);
}

function sourceList(passages) {
  const unique = [];
  for (const passage of passages) {
    if (!unique.some((item) => item.url === passage.url)) unique.push(passage);
  }
  return unique;
}

function linkSources(passages) {
  return sourceList(passages).map((source) => {
    const link = document.createElement("a");
    const url = new URL(source.url);
    // The index uses canonical production URLs, but a source link should stay
    // on whichever copy of the site a visitor is currently reviewing.
    link.href = `${url.pathname}${url.search}${url.hash}`;
    link.textContent = source.title;
    link.target = "_self";
    return link;
  });
}

function createAssistant() {
  const host = document.createElement("div");
  host.id = "site-assistant";
  host.setAttribute("aria-live", "polite");
  const shadow = host.attachShadow({ mode: "open" });
  shadow.innerHTML = `
    <style>
      :host { color: oklch(0.11 0.015 60); font-family: "Plus Jakarta Sans", sans-serif; }
      * { box-sizing: border-box; }
      button, input { font: inherit; }
      button { cursor: pointer; }
      .launcher { position: fixed; right: 18px; bottom: 18px; z-index: 20; border: 1px solid oklch(0.26 0.02 45); border-radius: 999px; padding: 11px 15px; background: oklch(0.18 0.02 55); color: oklch(0.98 0.006 80); font-size: 13px; font-weight: 600; letter-spacing: -.01em; box-shadow: 0 9px 28px oklch(0.11 0.02 55 / .18); }
      .launcher:hover, .launcher:focus-visible { background: oklch(0.3 0.13 22); outline: 2px solid oklch(0.58 0.12 30); outline-offset: 3px; }
      .panel { position: fixed; right: 18px; bottom: 70px; z-index: 20; display: grid; grid-template-rows: auto 1fr auto; width: min(410px, calc(100vw - 24px)); height: min(600px, calc(100svh - 102px)); overflow: hidden; border: 1px solid oklch(0.76 0.01 70); border-radius: 12px; background: oklch(0.98 0.006 80); box-shadow: 0 18px 54px oklch(0.14 0.02 50 / .18); }
      .panel[hidden] { display: none; }
      header { display:flex; justify-content:space-between; gap:12px; align-items:flex-start; padding:17px 18px 14px; border-bottom:1px solid oklch(0.88 0.006 80); }
      h2 { margin:0; font-size:15px; line-height:1.25; letter-spacing:-.015em; }
      header p { margin:3px 0 0; color:oklch(0.47 0.01 70); font-size:11px; line-height:1.45; }
      .close { width:28px; height:28px; border:0; border-radius:5px; background:transparent; color:oklch(0.37 0.01 70); font-size:20px; line-height:1; }
      .close:hover, .close:focus-visible { color:oklch(0.18 0.02 55); background:oklch(0.93 0.006 80); outline:none; }
      .messages { overflow-y:auto; padding:16px 18px; display:grid; align-content:start; gap:13px; }
      .message { max-width:92%; font-size:13px; line-height:1.55; white-space:pre-wrap; }
      .message.assistant { color:oklch(0.19 0.018 58); }
      .message.user { justify-self:end; padding:8px 11px; border-radius:9px; background:oklch(0.93 0.015 65); }
      .sources { display:flex; flex-wrap:wrap; gap:6px; margin-top:-8px; }
      .sources a { color:oklch(0.3 0.13 22); font-size:11px; text-decoration:none; border-bottom:1px dotted currentColor; }
      .sources a:hover { color:oklch(0.18 0.02 55); }
      .status { color:oklch(0.47 0.01 70); font-size:11px; font-style:italic; }
      .load { border:0; padding:0; background:none; color:oklch(0.3 0.13 22); font-size:12px; font-weight:600; text-align:left; }
      .load:hover { text-decoration:underline; }
      form { display:flex; gap:8px; padding:13px 14px; border-top:1px solid oklch(0.88 0.006 80); }
      input { min-width:0; flex:1; border:1px solid oklch(0.75 0.008 70); border-radius:6px; padding:9px 10px; background:oklch(0.995 0.004 80); color:inherit; font-size:13px; }
      input:focus { outline:2px solid oklch(0.56 0.1 30); outline-offset:1px; border-color:transparent; }
      form button { border:0; border-radius:6px; padding:8px 12px; background:oklch(0.3 0.13 22); color:oklch(0.98 0.006 80); font-size:12px; font-weight:600; }
      form button:hover, form button:focus-visible { background:oklch(0.18 0.02 55); outline:none; }
      form button:disabled, input:disabled { opacity:.6; cursor:wait; }
      @media (max-width: 520px) { .launcher { right:12px; bottom:12px; } .panel { right:12px; bottom:64px; width:calc(100vw - 24px); height:min(590px, calc(100svh - 82px)); } }
      @media (prefers-reduced-motion: reduce) { * { scroll-behavior:auto; } }
    </style>
    <button class="launcher" type="button" aria-expanded="false">Ask Eric</button>
    <section class="panel" hidden aria-label="Ask Eric">
      <header><div><h2>Ask Eric</h2><p>Local model. Site sources only.</p></div><button class="close" type="button" aria-label="Close assistant">×</button></header>
      <div class="messages" role="log"></div>
      <form><input aria-label="Ask a question about Eric Spencer" autocomplete="off" placeholder="What has Eric built?" /><button type="submit">Ask</button></form>
    </section>`;
  document.body.append(host);

  const launcher = shadow.querySelector(".launcher");
  const panel = shadow.querySelector(".panel");
  const close = shadow.querySelector(".close");
  const messages = shadow.querySelector(".messages");
  const form = shadow.querySelector("form");
  const input = shadow.querySelector("input");
  const submit = shadow.querySelector("form button");

  function say(text, type = "assistant", passages = []) {
    const message = document.createElement("div");
    message.className = `message ${type}`;
    message.textContent = text;
    messages.append(message);
    if (passages.length) {
      const sources = document.createElement("div");
      sources.className = "sources";
      for (const link of linkSources(passages)) sources.append(link);
      messages.append(sources);
    }
    messages.scrollTop = messages.scrollHeight;
    return message;
  }

  function status(text) {
    const line = document.createElement("div");
    line.className = "status";
    line.textContent = text;
    messages.append(line);
    messages.scrollTop = messages.scrollHeight;
    return line;
  }

  async function startModel() {
    if (engine) return engine;
    if (loading) return loading;
    if (!navigator.gpu) throw new Error("This browser does not offer WebGPU.");
    const line = status("Preparing the local model…");
    loading = (async () => {
      const webllm = await import("https://esm.run/@mlc-ai/web-llm");
      engine = await webllm.CreateMLCEngine(MODEL, {
        initProgressCallback: (report) => { line.textContent = report.text || "Preparing the local model…"; },
      });
      line.remove();
      say("Ready.");
      return engine;
    })();
    try { return await loading; } finally { loading = null; }
  }

  function showFallback(passages) {
    if (!passages.length) {
      say("No matching site source found.");
      return;
    }
    say(passages.slice(0, 3).map((item) => item.text).join("\n\n"), "assistant", passages);
  }

  async function ask(question) {
    const passages = relevant(question);
    say(question, "user");
    input.value = "";
    input.disabled = submit.disabled = true;
    try {
      const local = await startModel();
      if (!passages.length) {
        say("Not in the site sources.");
        return;
      }
      const sourceText = passages.map((item, index) => `[${index + 1}] ${item.title}\n${item.text}`).join("\n\n").slice(0, CONTEXT_LIMIT);
      const response = await local.chat.completions.create({
        messages: [
          { role: "system", content: `You are the private on-device assistant for ericspencer.us. Today is ${window.ERIC_SITE_KNOWLEDGE.updated}. Answer only from the supplied site passages. Be concise and factual. If the passages do not establish an answer, say so plainly. Never invent dates, credentials, contact details, claims, or links. Do not claim to be Eric.` },
          { role: "user", content: `Question: ${question}\n\nSite passages:\n${sourceText}` },
        ],
        temperature: 0.15,
        max_tokens: 350,
      });
      say(response.choices[0]?.message?.content?.trim() || "I could not form an answer from the retrieved site passages.", "assistant", passages);
    } catch (error) {
      showFallback(passages);
    } finally {
      input.disabled = submit.disabled = false;
      input.focus();
    }
  }

  launcher.addEventListener("click", () => {
    panel.hidden = !panel.hidden;
    launcher.setAttribute("aria-expanded", String(!panel.hidden));
    if (!panel.hidden && !messages.childElementCount) {
      say("Ask about research, projects, or experience. First use downloads the local model.", "assistant");
    }
    if (!panel.hidden) input.focus();
  });
  close.addEventListener("click", () => launcher.click());
  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const question = input.value.trim();
    if (question) ask(question);
  });
}

if (window.ERIC_SITE_KNOWLEDGE?.passages?.length) createAssistant();
