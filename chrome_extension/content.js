// Content Script: Extracts active page title, URL, selection, or full text
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "extract_page_content") {
    const selection = window.getSelection() ? window.getSelection().toString() : "";
    const pageData = {
      title: document.title,
      url: window.location.href,
      selected_text: selection,
      full_text: document.body.innerText ? document.body.innerText.substring(0, 5000) : ""
    };
    sendResponse(pageData);
  }
  return true;
});
