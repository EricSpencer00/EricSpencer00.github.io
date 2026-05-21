---
title: "tunes2tube"
date: 2026-05-15
description: "A local macOS app that drops a cover image and audio files in, and gives you back MP3s with the cover embedded as ID3v2 artwork — no account, no upload."
tags: ["Swift", "macOS"]
categories: ["Projects"]
draft: false
---

[GitHub Repo](https://github.com/EricSpencer00/tunes2tube-mac)

I wanted to attach a cover image to a handful of MP3s and could not find a way to do it that didn't involve uploading the files to some random web service, signing in with a Google account, or watching an ad for a "DRM-free converter." The thing I actually needed was about four lines of `ffmpeg`. So I wrapped it in a SwiftUI window and called it a day.

`tunes2tube-mac` is a macOS app (13+) that does exactly one thing: you drop a cover image into one slot, drop one or more audio files into another, optionally fill in album / artist / year, hit `⌘↩`, and it writes out `.mp3` files with the cover embedded as an ID3v2 APIC frame. The cover image itself is also copied into the output folder so you have a clean album-art file ready to use somewhere else. Output goes to `~/Music/Tunes2Tube/<Album-or-Artist>/` by default. If the input is already an MP3 the audio stream is copied with no re-encode; anything else gets `libmp3lame` at 320 kbps.

The name is a nod to [tunes2tube.com](https://www.tunes2tube.com/), which is the web tool I would have otherwise used. The original publishes the resulting video to YouTube, which is a nice feature but requires a Google OAuth client and a registered GCP project. Per my own project brief — anything that needs GCP gets dropped — I cut the YouTube piece entirely. The app's contract is "make tagged files; you decide where they go." If you want to publish, the README has the one-line `ffmpeg` command to turn the MP3 plus cover into a still-image video, and you upload that yourself.

## How it actually works

There is not much to it. The UI is a SwiftUI window with two drop zones and a small metadata form. A `@MainActor` view model (`ProcessingSession`) holds the state and drives `AudioProcessor`, which is a thin wrapper around `Foundation.Process` that shells out to `ffmpeg`. `ffmpeg` does the real work — read the audio, attach the cover as an APIC frame, write the MP3. The app looks for the binary at `/opt/homebrew/bin/ffmpeg`, `/usr/local/bin/ffmpeg`, or via `which ffmpeg`, and if it can't find one it surfaces a clear error instead of pretending the run succeeded.

Supported audio formats in, MP3 out: `mp3 wav flac m4a aac aiff ogg opus`. Supported cover formats: `.png`, `.jpg`, `.webp`. Per-file failures don't kill the batch — each track gets its own result and the UI shows you which ones made it.

There is also a `Makefile` that wraps `swift build` to produce a real `.app` bundle (Info.plist, ad-hoc codesigned). It won't be notarized, because that costs $99/year and this is a thing I built for myself in an evening.

## The local-first thing

This is a small project but it sits next to a habit I've been more deliberate about lately — see the [Private Whisper privacy work](/private-whisper-privacy.html) for the longer version. The pattern I keep running into is some entirely-mechanical task (transcribe audio, embed cover art, convert a file) that has perfectly capable local tooling on macOS, but the easiest discoverable option on Google is a website that wants your files on someone else's disk. There is no good reason an MP3 tagger should ever leave your machine. So when I need one and the existing local options are unfriendly or abandoned, I'm increasingly willing to write the SwiftUI shell myself.

## What's not done

It's MVP. The roadmap in the README is the honest list — per-track title editing (right now it uses the filename), a bitrate toggle for re-encoded inputs, an optional video output for the YouTube workflow (without the GCP piece), a universal binary release in GitHub Releases, and Sparkle auto-update if I ever care enough to set it up. PRs welcome — the codebase is small enough that you can read the whole thing in one sitting.
