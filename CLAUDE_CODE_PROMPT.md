# Build Leaseth Tenant Risk Scoring Frontend

## Context
Building the frontend for Leaseth - an AI-powered tenant risk assessment platform for landlords and property managers. This is a startup preparing for investor demos. The website must feel professional, trustworthy, and production-ready.

## Your Mission
Create a complete web frontend that connects to our deployed FastAPI backend and delivers tenant risk scores through an intuitive interface. The end result should impress investors and demonstrate real-world viability for property management professionals.

## Backend Integration
**API Base URL**: `https://sreejithm-leaseth-mvp.hf.space`

**Main Endpoint**: `POST /api/v1/score`

**Authentication**: JWT-based (Bearer tokens)

The backend is live on Hugging Face Spaces. You'll make standard fetch/axios calls to score applicants and retrieve results. All request/response schemas and field requirements are detailed in `FRONTEND_BRIEF.md`.

## What You're Building
A SaaS-style tenant screening platform with:
- Professional landing page explaining the value proposition
- Applicant input form that captures rental/financial data
- Real-time risk scoring with visual results
- Multi-applicant dashboard with analytics
- Mobile-responsive design throughout

The core flow: User inputs applicant data → API returns risk score (0-100) + recommendation (APPROVE/REJECT/REQUEST INFO) → Display results with professional visual treatment.

## Requirements Reference
See `FRONTEND_BRIEF.md` for complete specifications including:
- All input fields and validation rules
- Output display requirements and color coding
- Dashboard features and data visualization needs
- Trust/compliance elements
- Technical integration details


**Important**: Only reference `FRONTEND_BRIEF.md`, `CLAUDE.md`, `architecturalpatterns.md`, and `.github/copilot-instructions.md` - all project context is summarized there, no need to read other backend files.

## Critical Expectations
This is for investor presentation. It must:
- Look production-ready, not prototype
- Handle edge cases gracefully (loading, errors, empty states)
- Feel fast and responsive
- Build confidence in the technology
- Work flawlessly on mobile devices

The frontend is the face of the product. Investors will judge the entire platform by this interface.

## Collaboration Approach
We'll brainstorm together on implementation decisions, design choices, and feature prioritization. Bring your expertise on modern frontend best practices. Ask questions when specifications need clarification.

Build something that property managers would trust with real tenant decisions and investors would fund.
