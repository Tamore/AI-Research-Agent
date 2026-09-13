// Background Service Worker for Tab-Specific Chrome Side Panel
chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: false }).catch(() => {});

chrome.action.onClicked.addListener((tab) => {
  if (!tab || !tab.id) return;

  // In Chrome extensions, sidePanel.open must be triggered synchronously
  // within the user click gesture without preceding awaits.
  chrome.sidePanel.open({ tabId: tab.id }).catch((err) => {
    console.error("Failed to open side panel:", err);
  });

  // Ensure tab-specific options are configured
  chrome.sidePanel.setOptions({
    tabId: tab.id,
    path: "sidepanel.html",
    enabled: true
  }).catch(() => {});
});

console.log("CiteX Side Panel (Tab-scoped) initialized.");
