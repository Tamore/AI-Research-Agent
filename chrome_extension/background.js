// Background Service Worker for Tab-Specific Chrome Side Panel
const activeTabsWithPanel = new Set();

// Chrome's official method to open side panel on click without losing user gesture:
chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: true }).catch(() => {});

// Listen to tabs where user opens the panel
chrome.tabs.onActivated.addListener(async (activeInfo) => {
  // If the panel was opened for a specific set of tabs, disable on others
  if (activeTabsWithPanel.size > 0 && !activeTabsWithPanel.has(activeInfo.tabId)) {
    chrome.sidePanel.setOptions({
      tabId: activeInfo.tabId,
      enabled: false
    }).catch(() => {});
  }
});

chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status === "complete" && !activeTabsWithPanel.has(tabId)) {
    // Keep side panel default closed on fresh new tabs unless clicked
    chrome.sidePanel.setOptions({
      tabId: tabId,
      enabled: false
    }).catch(() => {});
  }
});

// Clean up closed tabs
chrome.tabs.onRemoved.addListener((tabId) => {
  activeTabsWithPanel.delete(tabId);
});

console.log("CiteX Side Panel (Tab-isolated) initialized.");
