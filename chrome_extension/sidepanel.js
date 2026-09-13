const API_BASE = "http://127.0.0.1:8000";

let state = {
  activeTab: null
};

document.addEventListener("DOMContentLoaded", async () => {
  checkApiHealth();
  extractActiveTabInfo();

  chrome.tabs.onActivated.addListener(() => {
    extractActiveTabInfo();
  });

  const parseBtn = document.getElementById("parseBtn");
  if (parseBtn) parseBtn.addEventListener("click", runResearch);

  const saveBtn = document.getElementById("saveNoteBtn");
  if (saveBtn) saveBtn.addEventListener("click", saveQuickNote);

  const closeBtn = document.getElementById("closeSidebarBtn");
  if (closeBtn) {
    closeBtn.addEventListener("click", () => {
      try {
        window.parent.postMessage({ action: "toggle_citex_sidebar" }, "*");
      } catch (err) {
        if (chrome && chrome.tabs) {
          chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
            if (tabs && tabs[0]) {
              chrome.tabs.sendMessage(tabs[0].id, { action: "toggle_citex_sidebar" });
            }
          });
        }
      }
    });
  }
});

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
    state.activeTab = currentTab;
    if (titleInput) titleInput.value = currentTab.title || currentTab.url || "Active Tab Context";
    if (topicInput) topicInput.value = currentTab.title || "";

    try {
      chrome.tabs.sendMessage(currentTab.id, { action: "extract_page_content" }, (response) => {
        if (chrome.runtime.lastError) return;
        if (response) {
          if (response.selected_text && topicInput) {
            topicInput.value = response.selected_text;
          }
          state.pageFullText = response.full_text || "";
        }
      });
    } catch (e) {
      console.log("Active tab content extractor bridge ready.");
    }
  });
}

async function runResearch() {
  const topic = document.getElementById("topicInput").value.trim();
  const parseBtn = document.getElementById("parseBtn");
  const box = document.getElementById("summaryOut");

  if (!topic) {
    document.getElementById("topicInput").focus();
    return;
  }

  parseBtn.disabled = true;
  parseBtn.innerText = "Synthesizing…";
  box.innerHTML = '<p class="mono" style="color:var(--color-accent)">Parsing page context and synthesizing detailed literature review…</p>';

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
      const data = await res.json();
      renderDetailedSynthesis(data);
    } else {
      showError("API error occurred while processing research request.");
    }
  } catch (err) {
    showError("Could not connect to local agent server at http://127.0.0.1:8000");
  } finally {
    parseBtn.disabled = false;
    parseBtn.innerText = "Parse & Summarize Tab";
  }
}

function renderDetailedSynthesis(r) {
  const box = document.getElementById("summaryOut");
  if (!box || !r) return;

  let bibtexSection = "";
  if (r.bibtex_citations) {
    bibtexSection = `\n\n### BibTeX Citation\n\`\`\`bibtex\n${r.bibtex_citations}\n\`\`\``;
  }

  let pdfLink = "";
  if (r.pdf_download_url) {
    pdfLink = `\n\n[Download Compiled IEEE Draft PDF](${API_BASE}${r.pdf_download_url})`;
  }

  const fullMarkdown = `${r.summary_markdown || ""}\n\n### Literature Comparison Matrix\n${r.literature_matrix || ""}${bibtexSection}${pdfLink}`;
  box.innerHTML = md(fullMarkdown);
}

function saveQuickNote() {
  const noteBtn = document.getElementById("saveNoteBtn");
  const topic = document.getElementById("topicInput").value.trim();
  const folderSelect = document.getElementById("folderSelect");
  let selectedFolder = folderSelect ? folderSelect.value : "General Research";

  if (selectedFolder === "+new") {
    const custom = prompt("Enter new folder name (e.g. Kyoto Univ Lab, Touch Displays):");
    if (custom && custom.trim()) {
      selectedFolder = custom.trim();
      const opt = document.createElement("option");
      opt.value = selectedFolder;
      opt.textContent = selectedFolder;
      opt.selected = true;
      folderSelect.insertBefore(opt, folderSelect.firstChild);
    } else {
      selectedFolder = "General Research";
      if (folderSelect) folderSelect.value = "General Research";
    }
  }

  chrome.tabs.query({ active: true, currentWindow: true }, async (tabs) => {
    if (tabs && tabs[0]) {
      const title = tabs[0].title || "Untitled Tab";
      const url = tabs[0].url || "";
      const noteContent = topic ? `Selection / Topic: ${topic}` : "";

      const noteItem = {
        title: title,
        url: url,
        folder: selectedFolder,
        note: noteContent,
        timestamp: new Date().toISOString()
      };

      chrome.storage.local.get({ citex_notes: [] }, (data) => {
        const notes = data.citex_notes;
        notes.unshift(noteItem);
        chrome.storage.local.set({ citex_notes: notes });
      });

      try {
        const res = await fetch(`${API_BASE}/api/v1/notes/synthesize`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            title: title,
            url: url,
            folder: selectedFolder,
            selected_text: topic,
            full_text: state.pageFullText || ""
          })
        });
        if (res.ok) {
          const data = await res.json();
          const pdfLink = data.pdf_download_url ? `\n\n[Download Compiled Note PDF](${API_BASE}${data.pdf_download_url})` : "";
          document.getElementById("summaryOut").innerHTML = md(`${data.notes_markdown}${pdfLink}`);
        } else {
          showBasicSaved();
        }
      } catch (e) {
        showBasicSaved();
      }

      function showBasicSaved() {
        const noteMarkdown = `## Saved Research Note\n- **Folder:** ${selectedFolder}\n- **Title:** ${title}\n- **URL:** [${url}](${url})\n${noteContent ? `\n> ${noteContent}\n` : ""}\n*Saved into folder notebook.*`;
        document.getElementById("summaryOut").innerHTML = md(noteMarkdown);
      }

      if (noteBtn) {
        const originalText = noteBtn.innerText;
        noteBtn.innerText = "Saved & Compiled PDF";
        setTimeout(() => { noteBtn.innerText = originalText; }, 2000);
      }
    }
  });
}

function md(src) {
  if (!src) return "";
  return window.marked ? window.marked.parse(src) : `<pre class="mono">${esc(src)}</pre>`;
}

function esc(s) {
  return String(s == null ? "" : s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

function showError(msg) {
  const box = document.getElementById("summaryOut");
  if (box) {
    box.innerHTML = `<div style="padding: 10px; border-left: 2px solid #a6595b; background: rgba(166, 89, 91, 0.08); color: #a6595b; font-family: var(--font-mono); font-size: 11.5px;">
      [Warning] ${esc(msg)}
    </div>`;
  }
}

