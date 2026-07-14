# Project profiles

Choose one primary profile and add others only when the product genuinely needs them.

## web-next-supabase

Recommended default for many full-stack web products.

Suggested:
- Next.js
- TypeScript
- Tailwind
- shadcn/ui if useful
- Supabase
- Playwright
- Vercel

External skills:
- frontend-design
- react-best-practices
- web-design-guidelines

## mobile-expo

Suggested:
- Expo
- React Native
- TypeScript
- Expo Router
- official Expo skills/plugin
- react-native-guidelines

Share domain types and API contracts with web when helpful. Do not force UI sharing where native experience would suffer.

## realtime-convex

Suggested when real-time state and fast reactive product iteration are central.

Choose Convex as the default data backend for that project rather than mixing it with Supabase without an ADR.

## research-heavy

Core:
- Perplexity MCP
- Firecrawl MCP
- Playwright MCP
- research-ledger skill

Use source ledgers and keep raw crawl output out of the main context.

## full-stack

Combine:
- web or mobile frontend,
- one primary backend,
- research stack,
- security gate,
- evaluator loop.

Keep agent count proportional to independent workstreams.
