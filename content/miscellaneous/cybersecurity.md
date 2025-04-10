+++
title = "Wireshark Network Analysis"
date = 2025-03-29
description = "Analysis of network traffic using Wireshark for COMP 301 Project 1."
draft = true
+++

## Overview

A comprehensive network traffic analysis using Wireshark to examine three PCAP files, investigating various protocols including TCP handshakes, FTP transfers, TELNET sessions, and HTTP traffic. This project demonstrates practical application of network security analysis tools and techniques.

---

## One.pcapng Analysis

### TCP Handshake Investigation

Using the filter `tcp.flags.syn == 1 && tcp.flags.ack == 0` to analyze initial connection attempts:

**Client Details:**
- IP: `192.168.100.70`
- MAC: `00:0c:29:1e:7a:da`

**Server Details:**
- IP: `192.168.100.111`
- MAC: `00:0c:29:41:bc:8b`

### FTP Activity Analysis

**Directory Operations:**
- Filter: `ftp.request.command == "MKD"`
- Found: Creation of "Passwords" directory (Packet #100)

**File Transfers:**
- Discovered via File → Export Objects → FTP-DATA:
  - Loyola.jpg (University logo)
  - usernames.txt
  - Additional text file

**Username List:**
```
Arnold
Alex
Abraham
Armin
Alejandro
```

**Additional Commands:**
- Filter: `ftp.request.command == "LIST" || ftp.request.command == "CWD" || ftp.request.command == "PWD"`
- Notable actions:
  - "CWD Files" (#36)
  - "CWD Passwords" (#103)

---

## Two.pcapng Analysis

### TELNET Session Investigation

**Login Details:**
- Server: armin
- Username: JohnSmith
- Password: password123
- Timestamp: Wednesday, March 25, 07:45:24 UTC 2020

**User Activities:**
1. Directory navigation
2. File manipulation in Passwords/
3. Text file editing
4. Directory creation
5. File movement operations

---

## Three.pcapng Analysis

### Web Traffic Investigation

**Notable Traffic:**
- Firefox.com detectportal
- AmazonS3 server communication
- Mozilla getpocket CDN
- Pearsonvue domain access

**Local Infrastructure:**
- Webserver IP: `192.168.100.70`
- DNS: Google (8.8.8.8)

### Media Content

**Audio:**
- File: NeverGiveUp.mp3 (Packet #5182)
- Content: Rick Roll audio
- Filter: `http.request.uri contains ".mp3"`

**Images:**
- hello.jpeg (Packet #5061)
- Baby Yoda image (Packet #5160)

### HTTP Analysis

**Redirects:**
- Filter: `http.response.code >= 300 && http.response.code < 400`
- Notable redirects:
  - sakai.luc.edu → https://sakai.luc.edu
  - gmail.com → www.google.com/gmail

**Authorization:**
- Filter: `http.authorization`
- Found credentials (Packet #5054):
  ```
  Authorization: Basic anNtaXRoOlBhc3N3MHJkMTIz
  Decoded: jsmith:Passw0rd123
  ```
