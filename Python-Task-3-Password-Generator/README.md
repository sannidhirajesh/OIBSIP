# OASIS Secure Password Generator

A Python Tkinter password generator built for the OASIS Python Programming Internship — Task 3, Advanced Tier.

## Features

- GUI built with Tkinter
- Password length control from 8 to 128
- Uppercase, lowercase, numbers and symbols
- At least one character from every selected type
- Cryptographically secure generation using Python `secrets`
- Password strength indicator
- Copy to Clipboard
- Exclude ambiguous characters
- Last 5 generated passwords shown for the current session
- Input validation and helpful error messages

## Run

No third-party packages are required.

### Option 1 — Terminal

```text
python app.py
```

### Option 2 — Windows

Double-click `run.bat`.

## Security

Passwords are generated using Python's `secrets` module rather than `random`.

Generated passwords are not saved to a file, database, or online service. The history is kept only in memory during the current application session and disappears when the application closes.

Do not share generated passwords.

## OASIS Task 3 Advanced Mapping

- GUI with length control and character selection: implemented
- `secrets` module: implemented
- Password strength indicator: implemented
- Selected-type enforcement: implemented
- Copy to Clipboard: implemented
- Ambiguous-character exclusion: implemented
- Last 5 session passwords: implemented
