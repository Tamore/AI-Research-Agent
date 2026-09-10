// Background Service Worker for handling Extension events and local API bridging
chrome.runtime.onInstalled.addListener(() => {
  console.log("AI Academic Research Assistant Extension installed successfully.");
});
