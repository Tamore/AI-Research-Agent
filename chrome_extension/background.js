// Chrome Extension Background Service Worker
// Tab-isolated side panel

chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: true }).catch(() => {});

// Listen for tab switches and close/hide panel if not desired
chrome.tabs.onActivated.addListener(async (activeInfo) => {
  // Let the side panel update its page context seamlessly
});

console.log("CiteX side panel service worker active.");
