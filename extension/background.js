// background.js
// Fired whenever a tab finishes loading:
chrome.webNavigation.onCompleted.addListener(({ tabId, frameId }) => {
  if (frameId === 0) {
    // only the top frame, not iframes
    chrome.scripting.executeScript({
      target: { tabId },
      files: ['contentScript.js']
    });
  }
});
