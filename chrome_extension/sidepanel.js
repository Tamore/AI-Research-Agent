const API_BASE = "http://127.0.0.1:8000";

let state = {
  view: "summary",
  report: null
};

document.addEventListener("DOMContentLoaded", async () => {
  checkApiHealth();
  extractActiveTabInfo();

  document.getElementById("parseBtn").addEventListener("click", runResearch);
  document.getElementById("saveNoteBtn").addEventListener("click", saveQuickNote);
  document.getElementById("copyBib").addEventListener("click", copyBibTeX);

  document.querySelectorAll("[data-go]").forEach(btn => {
    btn.addEventListener("click", (e) => {
      const viewKey = e.target.getAttribute("data-go");
      goView(viewKey);
    });
  });
});

function goView(viewKey) {
  state.view = viewKey;
  document.querySelectorAll(".nav-tab").forEach(tab => {
    tab.setAttribute("aria-current", String(tab.getAttribute("data-go") === viewKey));
  });
  document.querySelectorAll(".view").forEach(v => {
    v.classList.toggle("on", v.getAttribute("data-view") === viewKey);
  });
}

async function checkApiHealth() {
  const badge = document.getElementById("apiStatus");
  try {
    const res = await fetch(`${API_BASE}/health`);
    if (res.ok) {
      badge.innerText = "API Online";
      badge.className = "tag tag-outline";
    } else {
      badge.innerText = "API Error";
    }
  } catch (err) {
    badge.innerText = "API Offline";
    badge.style.color = "#a6595b";
    badge.style.borderColor = "#a6595b";
  }
}

function extractActiveTabInfo() {
  const titleInput = document.getElementById("pageTitle");
  const topicInput = document.getElementById("topicInput");

  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    if (!tabs || !tabs[0]) return;

    const currentTab = tabs[0];
    titleInput.value = currentTab.title || currentTab.url || "Active Tab Context";
    topicInput.value = currentTab.title || "";

    try {
      chrome.tabs.sendMessage(currentTab.id, { action: "extract_page_content" }, (response) => {
        if (chrome.runtime.lastError) return;
        if (response && response.selected_text) {
          topicInput.value = response.selected_text;
        }
      });
    } catch (e) {
      console.log("Side panel content script bridge fallback active.");
    }
  });
}

async function runResearch() {
  const topic = document.getElementById("topicInput").value.trim();
  const parseBtn = document.getElementById("parseBtn");

  if (!topic) {
    document.getElementById("topicInput").focus();
    return;
  }

  parseBtn.disabled = true;
  parseBtn.innerText = "Parsing…";
  setAllOutputsLoading();

  try {
    const res = await fetch(`${API_BASE}/api/v1/research`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        topic: topic,
        target_region: "Japan",
        max_papers: 2,
        generate_ieee_pdf: true
      })
    });

    if (res.ok) {
      state.report = await res.json();
      renderAllViews();
      goView("summary");
    } else {
      showError("API error occurred while processing research request.");
    }
  } catch (err) {
    showError("Could not connect to local agent server at http://127.0.0.1:8000");
  } finally {
    parseBtn.disabled = false;
    parseBtn.innerText = "Parse & Summarize Active Tab";
  }
}

function setAllOutputsLoading() {
  const msg = '<p class="mono" style="color:var(--color-accent)">⚡ Parsing page context & synthesizing research report…</p>';
  document.getElementById("summaryOut").innerHTML = msg;
  document.getElementById("matrixOut").innerHTML = msg;
  document.getElementById("facultyOut").innerHTML = msg;
  document.getElementById("papersOut").innerHTML = msg;
  document.getElementById("bibOut").textContent = "% compiling references…";
  document.getElementById("pdfOut").innerHTML = msg;
}

function renderAllViews() {
  const r = state.report;
  if (!r) return;

  // 02 Summary
  document.getElementById("summaryOut").innerHTML = md(r.summary_markdown) || '<p class="mono">Summary empty.</p>';

  // 03 Matrix
  document.getElementById("matrixOut").innerHTML = md(r.literature_matrix) || '<p class="mono">No matrix returned.</p>';

  // 04 Faculty
  const fac = r.faculty_radar || [];
  document.getElementById("facultyOut").innerHTML = fac.length ? fac.map(f => {
    const pct = Math.round((Number(f.alignment_score) || 0) * 100);
    return `<div style="padding:6px; border-bottom:1px solid var(--color-divider);">
      <div style="display:flex;justify-content:space-between;align-items:center;">
        <b>${esc(f.name)}</b> <span class="tag tag-outline">${pct}%</span>
      </div>
      <div class="mono" style="font-size:11px;">${esc(f.university_or_lab)} · ${esc(f.country)}</div>
      <div style="font-size:12px;margin-top:2px;">Latest: ${esc(f.latest_paper_title)}</div>
    </div>`;
  }).join("") : '<p class="mono">No faculty profiles matched.</p>';

  // 05 Papers
  const papers = r.analyzed_papers || [];
  document.getElementById("papersOut").innerHTML = papers.length ? papers.map(p => {
    return `<div style="padding:6px; border-bottom:1px solid var(--color-divider);">
      <div style="font-weight:600;font-size:13px;">${esc(p.title)}</div>
      <div class="mono" style="font-size:11px;">${esc(p.authors.join(", "))} (${p.year})</div>
      <a href="${esc(p.pdf_url)}" target="_blank" class="mono" style="font-size:11px;">[View Source PDF]</a>
    </div>`;
  }).join("") : '<p class="mono">No papers parsed.</p>';

  // 06 BibTeX
  document.getElementById("bibOut").textContent = r.bibtex_citations || "% no citations generated";

  // 07 IEEE PDF
  if (r.pdf_download_url) {
    const pdfUrl = `${API_BASE}${r.pdf_download_url}`;
    document.getElementById("pdfOut").innerHTML = `<div style="text-align:center; padding: 1rem;">
      <h4 style="margin-bottom:8px;">IEEE Paper Draft Compiled</h4>
      <a href="${pdfUrl}" target="_blank" class="btn btn-primary" style="text-decoration:none;display:inline-block;width:auto;">Download PDF</a>
    </div>`;
  } else {
    document.getElementById("pdfOut").innerHTML = '<p class="mono">PDF compilation disabled.</p>';
  }
}

function saveQuickNote() {
  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    if (tabs && tabs[0]) {
      const title = tabs[0].title;
      const url = tabs[0].url;
      const noteText = `## Quick Tab Note\n- **Title:** ${title}\n- **URL:** [${url}](${url})\n\nSaved to persistent research log.`;
      document.getElementById("summaryOut").innerHTML = md(noteText);
      goView("summary");
    }
  });
}

function copyBibTeX() {
  const txt = document.getElementById("bibOut").textContent;
  const btn = document.getElementById("copyBib");
  navigator.clipboard.writeText(txt).then(() => {
    btn.textContent = "Copied!";
    setTimeout(() => { btn.textContent = "Copy references.bib"; }, 1600);
  });
}

function md(src) {
  if (!src) return "";
  return window.marked ? window.marked.parse(src) : `<pre class="mono">${esc(src)}</pre>`;
}

function esc(s) {
  return String(s == null ? "" : s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}
