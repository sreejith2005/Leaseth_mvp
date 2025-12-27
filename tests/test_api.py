"""
Unit tests for API endpoints
"""

import pytest
from fastapi.testclient import TestClient
import asyncio

class TestAPIEndpoints:
    """Test FastAPI endpoints"""

    def test_health_check(self, test_client):
        """Test health check endpoint"""
        response = test_client.get("/api/v1/health")
        assert response.status_code in [200, 503]

    def test_root_endpoint(self, test_client):
        """Test root endpoint"""
        response = test_client.get("/")
        assert response.status_code == 200
        assert "name" in response.json()
        assert "version" in response.json()

    def test_register_endpoint_validation(self, test_client):
        """Test user registration validation"""
        # Test missing required fields
        response = test_client.post("/api/v1/auth/register", json={})
        assert response.status_code == 422

    def test_score_endpoint_invalid_input(self, test_client):
        """Test score endpoint with invalid input"""
        invalid_data = {
            "applicant_id": "APP_001",
            "name": "John Doe"
            # Missing required fields
        }
        response = test_client.post("/api/v1/score", json=invalid_data)
        assert response.status_code == 422
