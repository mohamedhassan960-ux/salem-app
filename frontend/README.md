# SALEM (سالم) — Arabic Conversational Tobacco Cessation Platform

SALEM (سالم) is a clinical evidence-grounded, human-centered Arabic conversational intervention application built to guide users through quitting smoking step-by-step.

> **Product Philosophy**: "سالم بيساعدني، مش بيقيّمني."

---

## 1. Features & Capabilities

- **Arabic-First True RTL Design System**: Tailored with Cairo font, high contrast light surfaces (`#F7F9FC` / `#FFFFFF`), and strict $\ge 44\times 44\text{px}$ touch targets.
- **Evidence-Grounded Conversational AI (WHO 2024)**: Direct clinical RAG grounding with zero technical jargon (no chunk IDs, embeddings, or similarity scores shown).
- **Behavioral Intervention & Craving Flow**: Multi-step urge management featuring 60-second delay timers, 4-7-8 breathing exercises, sensory disruption, and before/after check-ins.
- **Personal Quit Journey (Plan)**: Accurate smoke-free days and hours derived dynamically from `lastSmokedAt`, interactive daily tasks, and WHO clinical recovery milestones.
- **Multi-Tenant Security & Isolation**: Fully protected Supabase PostgreSQL schema with strict Row-Level Security (RLS) policies scoped per authenticated user (`auth.uid()`).
- **Offline & Low-Bandwidth Resilience**: Automatic synchronization between local storage cache and Supabase backend.

---

## 2. Tech Stack

- **Frontend**: React 18, TypeScript, Tailwind CSS, Vite
- **Design Tokens**: Custom Cairo typography scales, WCAG AA compliant palette
- **Backend API**: FastAPI RAG Pipeline (WHO 2024 Guidelines)
- **Database & Auth**: Supabase (PostgreSQL with RLS, GoTrue OAuth/Email Auth)
- **Icons**: Lucide React (Zero emojis in UI controls)

---

## 3. Environment Configuration

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Set your project variables:

```ini
VITE_SUPABASE_URL=https://your-project-id.supabase.co
VITE_SUPABASE_ANON_KEY=your-supabase-public-anon-key
VITE_API_BASE_URL=http://localhost:8000
```

---

## 4. Database Setup

Run the SQL migration script located in [`supabase_schema.sql`](file:///c:/Users/moham/OneDrive/Apps/اوكسجين/frontend/supabase_schema.sql) in your Supabase SQL Editor. It creates all tables and activates Row-Level Security (RLS) policies automatically.

---

## 5. Development & Production Build

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Run TypeScript typecheck and production build
npm run build

# Preview production build
npm run preview
```

---

## 6. Pre-Launch Verification Checklist

- [x] Design System & Color Palette Enforced (Light theme `#F7F9FC`)
- [x] Zero emojis in UI controls
- [x] Cairo font loaded and applied in true RTL layout
- [x] Google OAuth & Email authentication working
- [x] First-Time Onboarding (7 steps + draft saving)
- [x] Chat interface with WHO 2024 citation bottom sheet
- [x] Craving intervention flow (Timer + 4-7-8 Breathing + Check-in)
- [x] Compassionate relapse management without judgment
- [x] Personal Quit Plan with real milestone calculations
- [x] History, Profile, Settings, and Account Deletion
- [x] Zero secrets in client-side bundle
- [x] Clean build (`tsc -b && vite build` passing with 0 errors)
