# Inbox — Ash's always-on memory drop box

Drop any file here (notes, articles, screenshots, logs, audio, whatever) and Ash's consolidator job picks it up automatically.

- Supported: text, markdown, json, csv, images, audio, PDFs — basically anything.
- How it works: every couple hours the `ash-memory-consolidator` job reads new files here, extracts what's worth remembering into the daily note, then moves processed files to `processed/`.
- Just drop it and forget it. No need to tell Ash — he'll find it.
