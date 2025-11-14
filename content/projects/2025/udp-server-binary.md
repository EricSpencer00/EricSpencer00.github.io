---
title: "UDP server (binary)"
date: 2025-11-06
description: "Tiny UDP send/receive utilities for streaming and testing binary payloads — simple, reliable, and predictable."
tags: ["C++","UDP","Networking","Projects"]
categories: ["Projects"]
draft: false
---

![previews/udp-server-binary.png](/previews/udp-server-binary.png)

> Tiny tooling for sending and receiving raw binary over UDP. Built to test and reason about packetized streams without the noise of bespoke protocols.

I keep a soft spot in my projects folder for things that are deliberately small and predictable. This repo is one of those: a set of C/C++ utilities and scripts that make it trivial to send, receive, and verify binary payloads over UDP. It's not trying to replace robust file-transfer protocols — it's meant for testing, experimenting, and reproducing UDP behavior in a controlled way.

Repository: <https://github.com/EricSpencer00/UDP-server-binary>

## Why this exists

Sometimes you don't want TCP's reliability or a full-blown custom protocol when you're debugging packetization, ordering, or application-layer behavior. You want something that: binds to a port, sends raw bytes in discrete packets (or a stream), and gives you an easy way to verify the data arrived intact. That's this project in a sentence.

Use-cases:

- Reproducing packet loss/duplication scenarios.
- Testing recorder/consumer code that expects raw UDP payloads.
- Quick, scriptable binary transfers between machines on the same network.

## What's included

- Simple `udprecv` binary that binds to a UDP port, receives a packet, prints sender IP:port and raw payload, then exits.
- `udpsend_stream_file` which reads a file and sends it as a series of UDP packets with per-packet progress output.
- Small helper scripts, `makefile`, and test payloads (`test.bin`, `payload.bin`, etc.) so you can reproduce a run in seconds.

The codebase is intentionally compact — mostly C/C++ and a bit of shell glue — so it's easy to read and adapt.

## How it works (practical)

The workflow is short and obvious. On the receiver:

```bash
./bin/udprecv 9000
```

That binds the receiver to UDP port 9000 and waits for a single packet (it prints the sender and payload, then exits). From another terminal (or machine):

```bash
./bin/udpsend_stream_file 127.0.0.1 9000 test.bin
```

`udpsend_stream_file` sends `test.bin` as a sequence of UDP packets and prints progress as it goes. If you prefer to capture a full byte stream to disk rather than using the single-packet receiver, you can use `nc`/`socat`:

```bash
nc -u -l 9000 > received.bin
```

Then verify the transfer with a checksum:

```bash
shasum -a 256 test.bin received.bin
# compare outputs
```

If the checksums match, the bytes you sent are the bytes you got.

## Build

The repo includes a `makefile`. From the project root:

```bash
make
```

That produces the binaries under `bin/` (e.g., `udprecv`, `udpsend_stream_file`). No heavy dependencies.

## Notes, quirks, and things I like

- UDP is intentionally lossy — that's the point here. If you need guaranteed delivery, use TCP or something with acknowledgments.
- The tools are small and transparent. It's easy to add sequence numbers, timestamps, or custom headers if you want to experiment with ordering or reassembly.
- There are example payloads and logs in the repo so you can quickly run a known input and verify the output.

Sidenote: I appreciate tiny, single-purpose tools. They let you reason about a single problem at a time without other layers getting in the way.

## Possible next steps

- Add an optional sequence-prefix mode to `udpsend_stream_file` so receivers can detect missing packets.
- Add a simple receiver mode that writes all incoming packets to a stream file (instead of exiting after one packet) with timestamps for latency analysis.
- Wrap with a tiny Python harness for scripted tests (loss, reorder, duplicate) so you can run reproducible experiments.

## Try it

1. Clone the repo and build:

```bash
git clone https://github.com/EricSpencer00/UDP-server-binary.git
cd UDP-server-binary
make
```

2. In one terminal (receive):

```bash
./bin/udprecv 9000
```

3. In another terminal (send):

```bash
./bin/udpsend_stream_file 127.0.0.1 9000 test.bin
```

4. Or capture a stream and compare checksums:

```bash
nc -u -l 9000 > received.bin
shasum -a 256 test.bin received.bin
```

---

If you'd like, I can move this to `content/miscellaneous/` instead, add a preview image, or expand the "next steps" into a short how-to for adding sequence numbers and automated loss tests.

## Related: NASDAQ ITCH parser

This project sits in the same family — a compact, high-performance C implementation for parsing and replaying NASDAQ ITCH/ITTO feeds. It includes a timestamp-accurate replay server, a client/parser, and a sample-data generator.

Repo: <https://github.com/EricSpencer00/itch-parser-eric>

Quick start:

```bash
make
./generate_sample_itch
./itch_replay_server data/sample.itch 9999 1.0
./itch_client 127.0.0.1 9999
```

Why it matters: it's compact, fast, and practical — optimized big-endian readers, the 6-byte timestamp trick for cheap timestamp parsing, and replay timing for realistic tests. Good for backtests, order-book work, and market-data research.
