---
title: Leaseth Scoring API
emoji: 🏠
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
---

# Leaseth Tenant Risk Scoring API

Fast, reliable tenant risk assessment API powered by XGBoost.

## Endpoints

- **POST /api/score** - Score a tenant applicant
- **GET /health** - Health check
- **GET /docs** - API documentation (Swagger UI)

## Model

- XGBoost honest model
- 72.26% AUC
- 21 engineered features including:
  - Credit score
  - Income-to-rent ratio
  - Employment verification
  - Rental history
  - Payment patterns

## Features

- Real-time scoring (< 100ms)
- Three-tier risk classification (LOW/MEDIUM/HIGH)
- Actionable recommendations
- Confidence scores

Built for Leaseth MVP - 24/7 tenant screening powered by machine learning.
