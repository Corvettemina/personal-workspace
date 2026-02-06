# Bingo Board (Frontend Only)

This project is a Vite + React single-page app that runs entirely in the browser.
User accounts and bingo boards are stored in `localStorage`, so there is **no backend**
to deploy or manage.

## Getting Started

```bash
cd frontend
npm install
npm run dev
```

Open the URL printed by Vite (typically `http://localhost:5173`).

## Notes

- Login data and boards live only in your browser.
- Each username gets its own private board and stats view on this device.
- Boards are randomized per user and stay consistent across logins.
- Clearing site data or switching browsers will reset everything.
- The password hashing is client-side and intended for demo use only.
