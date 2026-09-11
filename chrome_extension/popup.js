const API_BASE = "http://127.0.0.1:8000";

let currentData = null;
let activeTabName = 'summary';

document.addEventListener("DOMContentLoaded", async () => {
  checkApiHealth();
  extractActiveTabInfo();

  document.getElementById("parseBtn").addEventListener("click", runResearch);
  document.getElementById("saveNoteBtn").addEventListener("click", saveQuickNote);

  document.querySelectorAll(".tab").forEach(tabEl => {
    tabEl.addEventListener("click", (e) => {
      document.querySelectorAll(".tab").forEach(t => t.classList.remove("active"));
      e.target.classList.add("active");
      activeTabName = e.target.getAttribute("data-tab");
      renderTabOutput();
    });
  });
});

async function checkApiHealth() {
  const badge = document.getElementById("apiStatus");
  try {
    const res = await fetch(`${API_BASE}/health`);
    if (res.ok) {
      badge.innerText = "API Online";
      badge.style.color = "#38bdf8";
    }
  } catch (err) {
    badge.innerText = "API Offline";
    badge.style.color = "#ef4444";
  }
}

function extractActiveTabInfo() {
  const titleInput = document.getElementById("pageTitle");
  const topicInput = document.getElementById("topicInput");

  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    if (!tabs || !tabs[0]) return;

    const currentTab = tabs[0];
    titleInput.value = currentTab.title || currentTab.url || "Active Tab";
    topicInput.value = currentTab.title || "";

    // Safely send message to content script
    try {
      chrome.tabs.sendMessage(currentTab.id, { action: "extract_page_content" }, (response) => {
        if (chrome.runtime.lastError) {
          // Content script not loaded on chrome:// or extension pages, ignore gracefully
          return;
        }
        if (response && response.selected_text) {
          topicInput.value = response.selected_text;
        }
      });
    } catch (e) {
      console.log("Extension content script bridge fallback active.");
    }
  });
}

async function runResearch() {
  const topic = document.getElementById("topicInput").value;
  const region = document.getElementById("regionInput").value;
  const maxPapers = parseInt(document.getElementById("maxPapers").value, 10) || 2;
  const outputContainer = document.getElementById("outputContainer");

  if (!topic) {
    document.getElementById("topicInput").focus();
    return;
  }

  outputContainer.innerHTML = '<p style="color:var(--accent-blue)">⚡ Executing research pipeline & parsing PDFs...</p>';

  try {
    const res = await fetch(`${API_BASE}/api/v1/research`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        topic: topic,
        target_region: region,
        max_papers: maxPapers,
        generate_ieee_pdf: true
      })
    });

    if (res.ok) {
      currentData = await res.json();
      renderTabOutput();
    } else {
      outputContainer.innerHTML = '<p style="color:#ef4444">Error executing research API.</p>';
    }
  } catch (err) {
    outputContainer.innerHTML = '<p style="color:#ef4444">Error: Could not connect to local agent server at http://127.0.0.1:8000</p>';
  }
}

function saveQuickNote() {
  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    if (tabs && tabs[0]) {
      const title = tabs[0].title;
      const url = tabs[0].url;
      const dateStr = new Date().toLocaleString();

      const noteText = `### 📝 Quick Research Note\n- **Title:** ${title}\n- **URL:** ${url}\n- **Saved:** ${dateStr}\n\n*Tab added to persistent research work log.*`;
      
      const outputContainer = document.getElementById("outputContainer");
      outputContainer.innerHTML = window.marked ? window.marked.parse(noteText) : `<pre>${noteText}</pre>`;
    }
  });
}

function renderTabOutput() {
  const container = document.getElementById("outputContainer");
  if (!currentData) {
    container.innerHTML = '<p style="color: var(--text-muted);">Ready. Click \'Synthesize Query\' or \'Quick Tab Note\' to extract academic insights.</p>';
    return;
  }

  if (activeTabName === 'summary') {
    container.innerHTML = window.marked ? window.marked.parse(currentData.summary_markdown || '') : `<pre>${currentData.summary_markdown}</pre>`;
  } else if (activeTabName === 'matrix') {
    container.innerHTML = window.marked ? window.marked.parse(currentData.literature_matrix || '') : `<pre>${currentData.literature_matrix}</pre>`;
  } else if (activeTabName === 'bibtex') {
    container.innerHTML = `<pre class="code-block">${currentData.bibtex_citations}</pre>`;
  } else if (activeTabName === 'pdf') {
    const pdfUrl = `${API_BASE}${currentData.pdf_download_url}`;
    container.innerHTML = `<div style="text-align:center; padding: 1.5rem 0.5rem;">
      <h4 style="margin-bottom:0.8rem; color:var(--text-main);">📄 IEEE Paper PDF Draft Compiled!</h4>
      <a href="${pdfUrl}" target="_blank" style="background:linear-gradient(135deg, var(--accent-blue), var(--accent-indigo)); color:#0b0f19; padding:0.6rem 1.2rem; text-decoration:none; font-weight:700; border-radius:6px; display:inline-block;">Download ieee_paper_draft.pdf</a>
    </div>`;
  }
}
