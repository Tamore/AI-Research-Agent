const API_BASE = "http://127.0.0.1:8000";

document.addEventListener("DOMContentLoaded", async () => {
  checkApiHealth();
  extractActiveTab();

  document.getElementById("parseBtn").addEventListener("click", runAgentResearch);
  document.getElementById("saveNoteBtn").addEventListener("click", saveTabNote);
});

async function checkApiHealth() {
  const dot = document.getElementById("apiDot");
  const label = document.getElementById("apiLabel");

  try {
    const res = await fetch(`${API_BASE}/health`);
    if (res.ok) {
      dot.classList.add("online");
      label.innerText = "API Online";
    }
  } catch (err) {
    dot.classList.remove("online");
    label.innerText = "API Offline";
  }
}

function extractActiveTab() {
  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    if (tabs[0]) {
      document.getElementById("pageTitle").value = tabs[0].title;
      document.getElementById("queryInput").value = tabs[0].title;

      chrome.tabs.sendMessage(tabs[0].id, { action: "extract_page_content" }, (response) => {
        if (response && response.selected_text) {
          document.getElementById("queryInput").value = response.selected_text;
        }
      });
    }
  });
}

async function runAgentResearch() {
  const query = document.getElementById("queryInput").value;
  const outputBox = document.getElementById("outputBox");

  if (!query) return;

  outputBox.innerText = "⚡ Agent executing research & PDF synthesis...";

  try {
    const res = await fetch(`${API_BASE}/api/v1/research`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        topic: query,
        target_region: "Japan",
        max_papers: 2,
        generate_ieee_pdf: true
      })
    });

    if (res.ok) {
      const data = await res.json();
      outputBox.innerText = `✅ SYNTHESIS COMPLETE!\n\n${data.summary_markdown}\n\n[BibTeX References Generated: ${data.bibtex_citations.length > 0 ? "Yes" : "No"}]`;
    } else {
      outputBox.innerText = "Error executing research API.";
    }
  } catch (err) {
    outputBox.innerText = "Error: Could not connect to local agent API server.";
  }
}

function saveTabNote() {
  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    if (tabs[0]) {
      const note = `[Note - ${new Date().toLocaleDateString()}]\nTitle: ${tabs[0].title}\nURL: ${tabs[0].url}\n`;
      document.getElementById("outputBox").innerText = "📝 Saved Tab Note:\n\n" + note;
    }
  });
}
