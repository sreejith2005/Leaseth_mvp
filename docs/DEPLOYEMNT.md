# Leaseth Deployment Guide

## Local Development

### Prerequisites
- Python 3.11+
- Conda or venv
- Git

### Setup
\`\`\`bash
# Clone repository
git clone <repo_url>
cd leaseth_mvp

# Create environment
conda create -n leaseth_env python=3.11
conda activate leaseth_env

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run server
uvicorn src.api:app --reload --host 0.0.0.0 --port 8000

# Access Swagger UI
# Visit http://localhost:8000/docs
\`\`\`

## Docker Deployment

### Build Image
\`\`\`bash
docker build -t leaseth:latest .
\`\`\`

### Run Container
\`\`\`bash
docker run -p 8000:8000 \
  -e DATABASE_URL=sqlite:///./leaseth.db \
  -v ./models:/app/models \
  leaseth:latest
\`\`\`

### Docker Compose
\`\`\`bash
docker-compose up -d
\`\`\`

## AWS Deployment

### EC2 Deployment
1. Launch EC2 instance
2. Install Docker
3. Push image to ECR
4. Run container

### ECS Deployment
1. Create task definition
2. Create ECS cluster
3. Deploy service
4. Configure load balancer

## Production Checklist

- [ ] Change JWT_SECRET in .env
- [ ] Enable HTTPS/SSL
- [ ] Set up PostgreSQL database
- [ ] Configure Redis cache
- [ ] Set up monitoring/alerting
- [ ] Enable rate limiting
- [ ] Set up backups
- [ ] Configure CI/CD pipeline
- [ ] Implement model drift detection
- [ ] Add fairness audit
