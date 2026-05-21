---
title: "iOS Soundboard"
date: 2025-08-14
description: "A SwiftUI soundboard app I built in an afternoon to get more comfortable with iOS."
tags: ["Swift", "iOS", "AI-written"]
categories: ["Projects"]
draft: false
---

This is the smallest possible thing I could build to keep poking at SwiftUI: a grid of buttons that each play an .mp3 when you tap one. Applause, bell, boing, pop, whoosh, click, beep, ding, buzz, chime, horn, tick, swoosh, ping, thud — fifteen sounds bundled into the app, plus a "premium" one (snap) sitting behind a lock icon I never actually wired up to StoreKit. The whole thing was a one-shot, written in a single sitting in mid-August.

The architecture is barely architecture. A `SoundData` `ObservableObject` holds the list of `SoundItem`s. A `SoundboardView` lays them out in a 3-column `LazyVGrid`. An `AudioService` plays the file when you tap. A `PurchaseService` pretends to gate the premium sound. That's basically it.

```swift
let columns = Array(repeating: GridItem(.flexible(), spacing: 10), count: 3)

LazyVGrid(columns: columns, spacing: 10) {
    ForEach(visibleSounds) { sound in
        SoundButton(
            sound: sound,
            audioService: audioService,
            isPremiumUnlocked: purchaseService.hasPurchasedPremium
        )
    }
}
```

I had been doing more iOS work for [fair-share](https://github.com/EricSpencer00/fair-share) and wanted to drill on the basics — `@StateObject`, `LazyVGrid`, sheets, `NavigationView` toolbars, `Image(systemName:)` — without the overhead of an actual product. A soundboard is the iOS equivalent of a TODO app: small enough to finish, big enough to touch most of the parts of the framework you'll need later.

There are two commits on the repo: "Initial Commit" and "oneshot". That's the whole history. I never shipped it to the App Store, the premium tier is fake, and the lock icon doesn't unlock anything. The mp3s are in `Soundboard/Sounds/`, the views are in `Soundboard/Views/`, and if you want to fork it and turn it into something real — go ahead. It's a perfectly fine starting point for a soundboard you actually care about.

[GitHub Repo](https://github.com/EricSpencer00/iOS-soundboard)

---

*Written with AI.*
