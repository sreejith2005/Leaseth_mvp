# Leaseth Tenant Risk Scoring - Frontend Brief

## Project
AI-powered tenant risk assessment system. Backend API scores rental applicants using dual XGBoost models, returns risk ratings and rental recommendations.

## API Integration
**Backend Deployment**: Hugging Face Spaces (Docker container, port 7860)

**Production URL**: `https://sreejithm-leaseth-mvp.hf.space`

**Endpoint**: `POST /api/v1/score`

**Usage**:
```javascript
const API_URL = "https://sreejithm-leaseth-mvp.hf.space/api/v1/score";

const response = await fetch(API_URL, {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify(applicantData)
});
```

**Authentication**: JWT Bearer token (15-min access, 7-day refresh)

**Core Files**:
- `src/api.py` - FastAPI endpoints, request/response schemas
- `src/database.py` - SQLAlchemy models (User, Application, Score)
- `src/auth.py` - JWT authentication logic

## Input Form Requirements
Single-page form with these fields:

**Personal Info**
- age (18-120)
- employment_status (employed | self-employed | unemployed)
- monthly_income (number)
- rental_history_years (number)

**Financial**
- credit_score (300-850)
- monthly_rent (number, max 2x income)
- on_time_payments_percent (0-100)

**Rental History**
- previous_evictions (number)
- lease_term_months (number)

**Verification**
- employment_verified (boolean/checkbox)
- income_verified (boolean/checkbox)

Real-time validation. Submit triggers API call.

## Output Display
Show immediately after scoring:

**Primary Metric**
- Risk Score: Large number 0-100 with color coding
  - 0-29: Green (LOW RISK)
  - 30-60: Yellow (MEDIUM RISK)  
  - 61-100: Red (HIGH RISK)

**Secondary Metrics**
- Risk Category: Badge/chip with color
- Recommendation: Clear action (APPROVE / REQUEST MORE INFO / REJECT)
- Confidence Score: Percentage bar (0-100%)

## Dashboard Features
Multi-applicant view showing:

- **Table/Grid**: All scored applicants with columns for name, score, category, date
- **Filters**: By risk category, date range, recommendation
- **Search**: By applicant name/ID
- **Stats Panel**: Total applications, avg score, approval rate
- **Export**: CSV download of results

## Design Direction
Clean, professional landlord/property manager aesthetic. Think SaaS dashboard - minimal, data-focused. Charts optional for MVP, prioritize table clarity. Mobile-responsive.

## Critical Additions for Investor Demo

**Landing Page**
- Hero section explaining value prop: "AI-Powered Tenant Screening in Seconds"
- Trust indicators: "ML Model Accuracy: 87%", "50K+ Data Points Trained"
- Clear CTA to dashboard/demo

**Professional Polish**
- Loading skeleton screens, not spinners
- Smooth transitions between states
- Empty states with helpful messaging, not blank screens
- Error boundaries with recovery actions
- Toast/snackbar notifications for actions

**Data Visualization**
- Risk score gauge/speedometer visual (not just number)
- Historical trend chart showing score distribution over time
- Pie chart: approval vs rejection rates
- Bar chart: applications by risk category
- These sell better than tables to non-technical investors

**Report Generation**
- PDF export of individual applicant report with logo
- Includes risk breakdown, key factors, recommendation
- Printable format for offline review
- Email report feature (even if mock)

**Applicant Comparison**
- Side-by-side comparison of 2-3 applicants
- Highlight differences in scores/factors
- "Best fit" indicator

**Trust & Compliance**
- Disclaimer footer: "AI assistant, not replacement for human judgment"
- "Fair Housing Compliant" badge (if accurate)
- Privacy policy link
- Data encryption indicator

**User Experience Gaps**
- No bulk upload shown (investors will ask about scale)
- No team/multi-user features (property managers need this)
- No applicant history tracking (repeat renters)
- No integration hooks (Zillow, RentSpree, etc. - show "Coming Soon")

**Visual Hierarchy Fixes**
- Risk score must dominate - make it 3x larger than anything else
- Use cards with shadows, not flat layouts
- Add micro-interactions (hover states, click feedback)
- Professional color palette (blues/grays, not primary colors)
- Custom icons, not emoji or stock

**What's Missing (Brutal)**
Your current spec is functional but boring. Investors don't fund boring. Add:
- Animated number counters when showing stats
- Progress indicators showing "Analyzing credit history... Employment data... Rental history..."
- Confidence explanation tooltip: "Why 89% confidence?"
- "Powered by XGBoost ML" badge
- Speed metric: "Scored in 1.2 seconds"
- Historical comparison: "23% lower risk than average applicant"

**Mobile-First Critical**
50% of landlords screen on phones. If demo isn't mobile-perfect, you lose credibility.

## Technical Notes
- Handle loading states during API calls
- Display error messages from API responses
- Store JWT in localStorage/sessionStorage
- Include request_id in error reporting
- Form should POST JSON matching `ApplicantRequest` schema in `src/api.py`
- Use optimistic UI updates where possible
- Implement proper skeleton loading states
- Add Sentry/error tracking integration ready
