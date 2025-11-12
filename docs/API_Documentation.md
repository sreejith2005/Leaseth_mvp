# Leaseth API Documentation

## Overview

This document provides complete API documentation for the Leaseth AI Scoring API.

## Authentication

### Login
**Endpoint:** `POST /api/v1/auth/login`

Request:
\`\`\`json
{
  "username": "user@example.com",
  "password": "password123"
}
\`\`\`

Response:
\`\`\`json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 900
}
\`\`\`

## Scoring Endpoint

### Score Single Applicant
**Endpoint:** `POST /api/v1/score`

**Authentication:** Required (Bearer token)

**Request Body:**
\`\`\`json
{
  "applicant_id": "APP_001",
  "name": "John Doe",
  "age": 35,
  "employment_status": "employed",
  "employment_verified": true,
  "income_verified": true,
  "monthly_income": 50000,
  "credit_score": 720,
  "previous_evictions": 0,
  "rental_history_years": 5,
  "on_time_payments_percent": 98,
  "late_payments_count": 1,
  "monthly_rent": 15000,
  "security_deposit": 30000,
  "lease_term_months": 12,
  "bedrooms": 2,
  "property_type": "apartment",
  "location": "Mumbai, MH",
  "market_median_rent": 18000,
  "local_unemployment_rate": 4.5,
  "inflation_rate": 5.2
}
\`\`\`

**Response (200 OK):**
\`\`\`json
{
  "status": "success",
  "request_id": "REQ_20251109_001",
  "timestamp": "2025-11-09T15:30:00Z",
  "data": {
    "score_id": 1,
    "applicant_id": "APP_001",
    "risk_score": 23,
    "risk_category": "LOW",
    "default_probability": 0.18,
    "recommendation": "APPROVE",
    "confidence_score": 0.87,
    "model_version": "V3_2025_11",
    "inference_time_ms": 85.2
  }
}
\`\`\`

## Health Check

**Endpoint:** `GET /api/v1/health`

**Response (200 OK):**
\`\`\`json
{
  "status": "healthy",
  "timestamp": "2025-11-09T15:30:00Z",
  "database": "connected",
  "models": "loaded",
  "api_version": "1.0.0"
}
\`\`\`

## Error Responses

### 400 Bad Request
\`\`\`json
{
  "status": "error",
  "error": "Invalid request data",
  "error_code": "BAD_REQUEST"
}
\`\`\`

### 401 Unauthorized
\`\`\`json
{
  "status": "error",
  "error": "Missing or invalid authentication token",
  "error_code": "UNAUTHORIZED"
}
\`\`\`

### 422 Validation Error
\`\`\`json
{
  "status": "validation_error",
  "errors": {
    "monthly_income": "monthly_income must be positive",
    "credit_score": "credit_score must be 300-850"
  }
}
\`\`\`

### 500 Server Error
\`\`\`json
{
  "status": "error",
  "error": "Internal server error",
  "error_code": "INTERNAL_ERROR"
}
\`\`\`

## Status Codes

- **200 OK** - Request successful
- **201 Created** - Resource created
- **400 Bad Request** - Invalid request
- **401 Unauthorized** - Missing/invalid auth
- **403 Forbidden** - Access denied
- **404 Not Found** - Resource not found
- **422 Unprocessable Entity** - Validation error
- **500 Server Error** - Internal error
- **503 Service Unavailable** - Service down

## Rate Limiting

Rate limiting will be enforced at 100 requests per minute per user.

Response headers include:
- `X-RateLimit-Limit`: Max requests per minute
- `X-RateLimit-Remaining`: Remaining requests
- `X-RateLimit-Reset`: Reset time

## Interactive Documentation

View interactive API documentation at `/docs` (Swagger UI) or `/redoc` (ReDoc).
