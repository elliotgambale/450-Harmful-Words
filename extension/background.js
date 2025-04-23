// background.js

chrome.webNavigation.onCompleted.addListener(({ tabId, frameId, url }) => {
  if (frameId !== 0) return;  // only top-level frame

  // skip chrome:// and other internal pages
  if (url.startsWith('chrome://') || url.startsWith('edge://') || url.startsWith('about:')) {
    return;
  }

  chrome.scripting.executeScript({
    target: { tabId },
    files: ['contentScript.js']
  });
});
