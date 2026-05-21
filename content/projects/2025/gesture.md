---
title: "Gesture"
date: 2025-08-01
description: "A proof of concept Jarvis-style macOS controller that takes voice commands and hand gestures from the webcam."
tags: ["Python", "macOS", "AI-written"]
categories: ["Projects"]
draft: false
---

This was me trying to see how far I could get with a Jarvis-style controller for my Mac in a single sitting. The idea was: webcam watches your hands, microphone listens for commands, and the two threads run side by side so you can either say "open Safari" or wave at the screen to trigger an action. Proof of concept — emphasis on proof of concept.

The whole thing is one `app.py` file with two functions running on separate threads. Voice control uses `SpeechRecognition` with Google's recognizer for transcription, then shells out to `osascript` or the macOS `say` command to actually do things. Right now it knows how to open Safari and tell you the time. That's it. Everything else falls through to "Command not recognized." It was never meant to be more than a scaffold for adding more handlers — I just never came back to add them.

Gesture control uses OpenCV plus MediaPipe to pull hand landmarks from the webcam feed, and `pyautogui` to fire keystrokes. The current "gesture" is checking whether the tip of your index finger (landmark 8) is above your wrist (landmark 0), and if so, hitting spacebar. So you can pause a YouTube video by pointing up at your screen. There's a one-second `time.sleep` after each trigger to keep it from firing fifty times per raised finger.

```python
index_tip = hand_landmarks.landmark[8]
wrist = hand_landmarks.landmark[0]
if index_tip.y < wrist.y:
    pyautogui.press('space')
    time.sleep(1)
```

There's also a `stubs.py` that exists for the sole purpose of forcing `modulegraph` to detect `rubicon.objc` when bundling the thing into a `.app` with `py2app`, which was its own little side quest. macOS does not love it when you try to ship a Python app that wants webcam and microphone access.

The honest list of what doesn't work: there's no real command grammar (just two hardcoded `if` branches), no gesture vocabulary beyond "finger up = space," no error recovery if the webcam isn't accessible, and if you actually want it to feel like Jarvis you'd want some kind of wake word so it isn't transcribing every word you say all day. I'd want to swap Google's recognizer for something local like Vosk too — sending every utterance to Google's API is not the move.

It was a fun afternoon of seeing how few moving parts you actually need to do the basic version of this. If you want to fork it and add a real gesture set, [GitHub Repo](https://github.com/EricSpencer00/Gesture).

---

*Written with AI.*
