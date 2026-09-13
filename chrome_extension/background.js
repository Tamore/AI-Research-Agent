// Background Service Worker for Tab-Specific Chrome Side Panel
const activeTabsWithPanel = new Set();

chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: false }).catch(() => {});

chrome.action.onClicked.addListener(async (tab) => {
  if (!tab || !tab.id) return;

  activeTabsWithPanel.add(tab.id);

  // Enable and open side panel exclusively for this tab
  await chrome.sidePanel.setOptions({
    tabId: tab.id,
    path: "sidepanel.html",
    enabled: true
  });

  chrome.sidePanel.open({ tabId: tab.id }).catch((err) => {
    console.error("Failed to open side panel:", err);
  });
});

// When user switches tabs, if the newly active tab was never activated for CiteX, disable it
chrome.tabs.onActivated.addListener(async (activeInfo) => {
  if (!activeTabsWithPanel.has(activeInfo.tabId)) {
    chrome.sidePanel.setOptions({
      tabId: activeInfo.tabId,
      enabled: false
    }).catch(() => {});
  }
});

// Clean up closed tabs
chrome.tabs.onRemoved.addListener((tabId) => {
  activeTabsWithPanel.delete(tabId);
});

console.log("CiteX Side Panel (Tab-isolated) initialized.");
