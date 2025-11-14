---
title: "UDP server (binary)"
date: 2025-11-06
description: "UDP send/receive utilities for binary payloads."
tags: ["C++","UDP","Networking","Projects"]
categories: ["Projects"]
draft: false
---

![previews/udp-server-binary.png](/previews/udp-server-binary.png)

## Repository

<https://github.com/EricSpencer00/UDP-server-binary>

## Tools

- `udprecv`: Binds to a UDP port, receives one packet, prints sender and payload.
- `udpsend_stream_file`: Sends a file as UDP packets.

## Commands

```bash
make
./bin/udprecv 9000
./bin/udpsend_stream_file 127.0.0.1 9000 test.bin
nc -u -l 9000 > received.bin
shasum -a 256 test.bin received.bin
```

## Build

- `make` produces binaries in `bin/`.

## Notes

- UDP is lossy.
- Extendable for sequence numbers or timestamps.

## Related

- NASDAQ ITCH parser: <https://github.com/EricSpencer00/itch-parser-eric>
