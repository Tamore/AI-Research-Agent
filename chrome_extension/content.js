// Content Script: Tab-isolated Sliding Right Sidebar (Claude-style)
let sidebarIframe = null;

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "extract_page_content") {
    const selection = window.getSelection() ? window.getSelection().toString() : "";
    sendResponse({
      title: document.title,
      url: window.location.href,
      selected_text: selection,
      full_text: document.body.innerText ? document.body.innerText.substring(0, 5000) : ""
    });
  } else if (request.action === "toggle_citex_sidebar") {
    toggleSidebar();
    sendResponse({ status: "toggled" });
  }
  return true;
});

function toggleSidebar() {
  if (!sidebarIframe) {
    sidebarIframe = document.createElement("iframe");
    sidebarIframe.id = "citex-sidebar-frame";
    sidebarIframe.src = chrome.runtime.getURL("sidepanel.html");
    
    // Style the in-page sidebar drawer (docked directly on right edge)
    Object.assign(sidebarIframe.style, {
      position: "fixed",
      top: "0",
      right: "0",
      width: "420px",
      height: "100vh",
      zIndex: "2147483647", // Maximum z-index
      border: "none",
      borderLeft: "1px solid rgba(29, 31, 32, 0.18)",
      boxShadow: "-8px 0 24px rgba(0, 0, 0, 0.15)",
      backgroundColor: "#f2f2f3",
      transition: "transform 0.25s cubic-bezier(0.16, 1, 0.3, 1)",
      transform: "translateX(0)"
    });

    document.documentElement.appendChild(sidebarIframe);
  } else {
    // Toggle slide in/out
    if (sidebarIframe.style.transform === "translateX(0px)" || sidebarIframe.style.transform === "translateX(0)") {
      sidebarIframe.style.transform = "translateX(100%)";
    } else {
      sidebarIframe.style.transform = "translateX(0)";
    }
  }
}
