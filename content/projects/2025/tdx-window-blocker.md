---
title: "TDX Window Blocker"
date: 2025-03-08
description: "Custom Safari Script for TDX Popups"
tags: ["iOS", "JavaScript"]
categories: ["Projects", "Web"]
draft: false
---

TDX creates a new window whenever you click a new Ticket/User/etc. This script, paired with "Stay for Safari," blocks the new window from appearing and instead opens it within the current window in a modal container.

Key features include:
- Overriding `openWin` to display content in a modal overlay.
- Removing `openWinHref` onclick attributes dynamically.
- Compatibility with Safari using the Stay for Safari extension.

## How to Install `script.js` on Safari Using Stay for Safari

### Prerequisites
- macOS with Safari installed
- Stay for Safari extension installed from the [App Store](https://apps.apple.com/us/app/stay-for-safari/id1591620171)
- `script.js` file ready for installation

### Steps

#### 1. Install Stay for Safari
1. Open the [Stay for Safari](https://apps.apple.com/us/app/stay-for-safari/id1591620171) page on the App Store.
2. Click on the "Get" button to download and install the extension.
3. Once installed, open Safari and go to `Preferences` > `Extensions`.
4. Enable the Stay for Safari extension.

#### 2. Open Stay for Safari
1. Click on the Stay for Safari icon in the Safari toolbar.
2. Select "Manage Scripts" from the dropdown menu.

#### 3. Add `script.js`
1. In the Stay for Safari interface, click on the "+" button to add a new script.
2. Enter a name for your script (e.g., `My Custom Script`).
3. Copy the contents of the `script.js` file found [here](https://github.com/EricSpencer00/WindowBlockerForTDX-MacOS/blob/main/script.js) and paste it into the script editor.
4. Specify the TDX URL in the 6th line of the script.

#### 4. Save and Activate the Script
1. Click the "Save" button to save your script.
2. Ensure that the script is enabled by checking the toggle switch next to the script name.

#### 5. Verify the Script
1. Navigate to a website where your script should run.
2. Open the browser console (Option + Command + C) to verify that the script is executing correctly.

### Conclusion
You have successfully installed and activated `script.js` on Safari using the Stay for Safari extension. You can now enjoy the custom functionality provided by your script on the specified websites.

[GitHub Repo](https://github.com/EricSpencer00/WindowBlockerForTDX-MacOS)