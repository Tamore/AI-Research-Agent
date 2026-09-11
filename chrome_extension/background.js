// Background Service Worker for Chrome Side Panel & API Bridge
chrome.runtime.onInstalled.addListener(() => {
  chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: true })
    .catch((error) => console.error("Error setting panel behavior:", error));
  console.log("AI Academic Research Side Panel installed successfully.");
});
