// Chrome Extension Background Service Worker
// Enables side panel ONLY on the specific tab when clicked

chrome.runtime.onInstalled.addListener(() => {
  // Disable side panel globally by default
  chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: false }).catch(() => {});
  chrome.sidePanel.setOptions({ enabled: false }).catch(() => {});
});

chrome.action.onClicked.addListener(async (tab) => {
  if (!tab || !tab.id) return;

  // 1. Enable the side panel ONLY for this specific tab ID
  await chrome.sidePanel.setOptions({
    tabId: tab.id,
    path: "sidepanel.html",
    enabled: true
  });

  // 2. Open it for this tab ID
  await chrome.sidePanel.open({ tabId: tab.id });
});

console.log("CiteX tab-isolated side panel ready.");
