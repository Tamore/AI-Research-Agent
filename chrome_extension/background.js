// Background Service Worker for Tab-Specific Chrome Side Panel
chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: false }).catch(() => {});

chrome.action.onClicked.addListener(async (tab) => {
  if (!tab || !tab.id) return;

  // Enable side panel ONLY for this specific tab
  await chrome.sidePanel.setOptions({
    tabId: tab.id,
    path: "sidepanel.html",
    enabled: true
  });

  // Open the side panel specifically for this tab
  await chrome.sidePanel.open({ tabId: tab.id });
});

console.log("AI Academic Research Side Panel (Tab-scoped) initialized.");
