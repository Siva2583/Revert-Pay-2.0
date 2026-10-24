# RevertPay frontend

React 19 + Vite frontend for the RevertPay escrow and ledger workspace.

## Run locally

```sh
npm ci
npm run dev
```

The development server proxies `/api` requests to the existing Spring Boot backend at `http://localhost:8080`. Authentication continues to use the existing JWT and local-storage behavior.

## Quality checks

```sh
npm run lint
npm run test:render
npm run build
```

`test:render` is a dependency-free server-render smoke check for the active screen components. It does not replace browser or backend integration testing.

## Structure

- `src/App.jsx` — existing state-based page navigation and session handling
- `src/components/` — screens and shared UI primitives
- `src/hooks/` — request lifecycle and duplicate-submission protection
- `src/services/` — existing API paths and native-fetch request helper
- `src/utils/` — formatting, role, navigation, and escrow helpers
- `src/index.css` — design tokens, local font stacks, and global foundation
- `src/App.css` — shared component and responsive styles
- `src/styles/editorial.css` — editorial authentication and workspace art direction
- `src/assets/` — optimized local editorial artwork

Manrope and IBM Plex Mono are served locally through Fontsource; the interface does not depend on a third-party font CDN.

No API paths, authentication semantics, backend files, or financial business rules are changed by the frontend design system.
