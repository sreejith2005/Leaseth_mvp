# Leaseth - AI Tenant Risk Scoring System

Leaseth is an intelligent tenant risk assessment platform powered by XGBoost machine learning models. It provides landlords and property managers with data-driven, objective tenant risk scores in seconds.

## Features

- **Dual-Model Hybrid System**: Separate models for applicants with and without eviction history
- **Real-Time Scoring**: <200ms inference time
- **Explainable AI**: SHAP-based feature importance and prediction explanations
- **Fair Housing Compliance**: Designed for regulatory requirements
- **Easy Integration**: Simple REST API with comprehensive documentation
- **Audit Trail**: Complete audit logs for compliance
- **User Authentication**: JWT-based security

## Quick Start

### Installation

Clone repository
git clone https://github.com/sreejith2005/Leaseth_mvp.git
cd leaseth_mvp

Create Python environment
conda create -n leaseth_env python=3.11
conda activate leaseth_env

Install dependencies
pip install -r requirements.txt

Setup environment
cp .env.example .env

text

### Running the API

Start FastAPI server
python run_api.py

Access API documentation
Swagger UI: http://localhost:8000/docs
ReDoc: http://localhost:8000/redoc
text

### Testing

Visit http://localhost:8000 and use the interactive API documentation to test endpoints.

## API Usage

### Score an Applicant

curl -X POST http://localhost:8000/api/v1/score
-H "Content-Type: application/json"
-H "Authorization: Bearer YOUR_TOKEN"
-d '{
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
}'

text

## Project Structure

leaseth_mvp/
├── src/
│ ├── api.py # FastAPI endpoints
│ ├── features.py # Feature engineering
│ ├── scoring.py # Model routing & prediction
│ ├── auth.py # Authentication
│ └── database.py # Database models
├── models/ # Trained XGBoost models
├── frontend/ # HTML/React frontend
├── tests/ # Unit tests
├── config/ # Configuration
├── docs/ # Documentation
├── requirements.txt # Python dependencies
├── .env.example # Environment template
└── README.md # This file

text

## Documentation

- [API Documentation](docs/API_DOCUMENTATION.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [GitHub Copilot Context](.copilot-instructions.md)

## Development Roadmap

### Phase 1-2: MVP Backend ✅
- [x] Dual XGBoost models
- [x] FastAPI endpoints
- [x] User authentication
- [x] Database integration

### Phase 3: Test Interface 🔄
- [ ] HTML/CSS/JS test form
- [ ] Bulk CSV scoring
- [ ] Results dashboard

### Phase 4: Professional Frontend 📋
- [ ] React application
- [ ] User dashboard
- [ ] Analytics

### Phase 5: Production Ready 🚀
- [ ] PostgreSQL migration
- [ ] Redis caching
- [ ] AWS deployment
- [ ] Monitoring & alerts

## Technology Stack

- **Backend**: FastAPI, Python 3.11
- **ML**: XGBoost, SHAP
- **Database**: SQLite (MVP), PostgreSQL (Production)
- **Frontend**: React (Planned)
- **Deployment**: Docker, AWS

## Contributing

Contributions are welcome! Please follow these guidelines:
1. Create a feature branch
2. Make your changes
3. Write/update tests
4. Submit a pull request

## License

This project is licensed under the MIT License.

## Contact

For questions or support, contact: support@leaseth.ai

## Disclaimer

This tool is for informational purposes only. Use with appropriate legal and compliance review.