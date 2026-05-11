# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

A bash script that automates remote torrent downloading: uploads a `.torrent` file to a remote server running Deluge, polls until the download completes, then pulls the finished files back locally via SCP.

## Setup

```bash
cp config.example config   # then edit with real HOST / SSH_PORT
```

`config` is gitignored — it holds the live server details.

## Usage

```bash
./sync <path-to-.torrent-file>
```

## Architecture

- **`sync`** — Main executable. Uses SSH multiplexing for efficient repeated connections. Flow: validate input → verify remote (deluge-console installed, deluged running) → upload .torrent → add to Deluge → poll for completion → SCP result back locally.
- **`config`** — Sourced by `sync`. Defines `HOST`, `SSH_PORT`, `REMOTE_DOWNLOAD_DIR`, `LOCAL_DOWNLOAD_DIR`, `POLL_INTERVAL`.

The script relies on `deluge-console` on the remote host and parses its `info` output to extract torrent name, hash, state, and progress.
