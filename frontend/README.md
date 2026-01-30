# Leaseth Frontend

React + Vite frontend for Leaseth AI-Powered Tenant Risk Scoring Platform.

## Tech Stack

- **React 18** - UI framework
- **Vite 5** - Build tool
- **TypeScript** - Type safety
- **TailwindCSS** - Styling
- **Recharts** - Charts and visualizations
- **Lucide React** - Icons
- **Zod** - Form validation
- **React Router** - Client-side routing

## Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

```bash
cd frontend
npm install
```

### Development

```bash
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) to view in browser.

### Build

```bash
npm run build
```

Builds to `dist/` folder.

### Preview Production Build

```bash
npm run preview
```

## Project Structure

```
frontend/
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── ui/              # Base components (Button, Card, Input, etc.)
│   │   ├── Hero.tsx         # Landing page hero section
│   │   ├── TrustIndicators.tsx
│   │   ├── HowItWorks.tsx
│   │   ├── FormSection.tsx
│   │   ├── RiskGauge.tsx    # Animated risk score gauge
│   │   ├── LoadingAnalysis.tsx
│   │   ├── RecommendationCard.tsx
│   │   ├── ApplicantTable.tsx
│   │   ├── StatsPanel.tsx
│   │   ├── Charts.tsx       # Recharts visualizations
│   │   ├── Toast.tsx
│   │   ├── ErrorBoundary.tsx
│   │   └── EmptyState.tsx
│   ├── pages/
│   │   ├── Landing.tsx      # Home page
│   │   ├── ScoringForm.tsx  # Applicant input form
│   │   ├── Results.tsx      # Risk assessment results
│   │   └── Dashboard.tsx    # Analytics dashboard
│   ├── services/
│   │   └── api.ts           # API client for backend
│   ├── hooks/
│   │   ├── useForm.ts       # Form state management
│   │   └── useLocalStorage.ts
│   ├── utils/
│   │   └── validation.ts    # Zod validation schemas
│   ├── data/
│   │   └── demoApplicants.ts # Pre-seeded demo data
│   ├── types/
│   │   └── index.ts         # TypeScript interfaces
│   ├── App.tsx
│   ├── main.tsx
│   └── index.css            # Tailwind + custom styles
├── public/
├── package.json
├── vite.config.ts
├── tailwind.config.js
└── vercel.json              # Vercel deployment config
```

## Features

### Landing Page
- Hero section with value proposition
- Trust indicators (accuracy, speed, data points)
- How it works 3-step flow
- Call-to-action sections

### Scoring Form
- Multi-section form with real-time validation
- Personal, financial, employment, rental history, property sections
- Credit score slider (300-850)
- Rent-to-income validation

### Results Page
- Animated risk score gauge (0-100)
- Risk category badge (LOW/MEDIUM/HIGH)
- Recommendation display (APPROVE/MANUAL_REVIEW/REJECT)
- Confidence score
- AI reasoning explanation
- Risk factor breakdown

### Dashboard
- Stats overview (total applications, avg score, approval rate)
- Risk distribution pie chart
- Recommendation bar chart
- Score distribution histogram
- Filterable/sortable applicant table
- Search by name, location, or ID
- Pre-seeded demo data

## API Integration

Connects to the Leaseth backend at:
```
https://sreejithm-leaseth-mvp.hf.space/api/score
```

### Request Format
```typescript
interface ApplicantInput {
  applicant_id: string
  name: string
  age: number
  monthly_income: number
  credit_score: number
  monthly_rent: number
  employment_status: 'employed' | 'self-employed' | 'unemployed'
  // ... more fields
}
```

### Response Format
```typescript
interface ScoringResponse {
  applicant_id: string
  risk_score: number
  risk_category: 'LOW' | 'MEDIUM' | 'HIGH'
  recommendation: 'APPROVE' | 'MANUAL_REVIEW' | 'REJECT'
  confidence: number
  reasoning: string
  processing_time_ms: number
}
```

## Deployment

### Vercel (Recommended)

1. Push to GitHub
2. Import project in Vercel
3. Set build command: `npm run build`
4. Set output directory: `dist`
5. Deploy

### Manual

Build and serve the `dist/` folder with any static file server.

## Color Palette

- **Primary Navy**: `#1e3a5f` - Trust, professionalism
- **Low Risk**: `#10b981` (Emerald)
- **Medium Risk**: `#f59e0b` (Amber)
- **High Risk**: `#f43f5e` (Rose)
- **Background**: Slate grays

## License

Proprietary - Leaseth
