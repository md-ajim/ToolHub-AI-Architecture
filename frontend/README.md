# Frontend — AI-Powered Utility Platform

Next.js frontend for the AI-Powered Utility Platform.

## Stack

- Next.js 16 (App Router)
- React 19
- TypeScript
- Tailwind CSS 4
- shadcn/ui

## Folder Structure

```
frontend/
  src/
    app/           Routes and pages (tools, category, dashboard, pricing, auth)
    components/    Shared UI components (layout, tool, ui, cards, charts, ...)
    features/      Feature modules (ai, analytics, auth, dashboard, image, pdf, ...)
    hooks/         Shared React hooks
    lib/           Core utilities (api, auth, metadata, query-client, storage, ...)
    services/      API service clients (auth, image, pdf, subscription, ...)
    store/         Client state
    types/         Shared TypeScript types
    utils/         Helpers
    middleware.ts  Route protection
```

## Getting Started

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## Environment Variables

- `NEXT_PUBLIC_API_URL` — backend API base URL (e.g. `http://localhost:8000/api/v1`)

See `../.env.example`.

## Scripts

- `npm run dev` — development server
- `npm run build` — production build
- `npm run start` — serve production build
- `npm run lint` — ESLint

## Notes

This version of Next.js introduces breaking changes compared to earlier versions. Read the guides in `node_modules/next/dist/docs/` before writing Next.js-specific code (see `AGENTS.md`).

## Documentation

Always follow the project documentation (`../docs/`) — start with `docs/00-README_FOR_AI.md`.
