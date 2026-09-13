// Background Service Worker for Tab-Isolated In-Page Sidebar
chrome.action.onClicked.addListener(async (tab) => {
  if (!tab || !tab.id) return;

  try {
    // Send toggle message to the active tab's content script
    await chrome.tabs.sendMessage(tab.id, { action: "toggle_citex_sidebar" });
  } catch (err) {
    // If content script is not yet injected (e.g. freshly opened page), inject and toggle
    await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      files: ["content.js"]
    });
    chrome.tabs.sendMessage(tab.id, { action: "toggle_citex_sidebar" }).catch(() => {});
  }
});

console.log("CiteX tab-isolated in-page sidebar worker ready.");
