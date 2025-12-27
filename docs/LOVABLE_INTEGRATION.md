# Connecting Lovable Dashboard to Your Model

## Step 1: Start Your API

```powershell
# Install dependencies (if not already installed)
pip install fastapi uvicorn

# Run the simple API
python simple_api.py
```

API will run on: `http://localhost:8000`

Test it works: `http://localhost:8000/docs` (Swagger UI)

---

## Step 2: In Lovable - Create the API Call

In your Lovable dashboard component, add this code:

```typescript
// API Configuration
const API_URL = "http://localhost:8000/api/score";

// Function to score applicant
async function scoreApplicant(applicantData) {
  try {
    const response = await fetch(API_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        applicant_id: applicantData.id,
        name: applicantData.name,
        age: applicantData.age,
        monthly_income: applicantData.income,
        credit_score: applicantData.creditScore,
        monthly_rent: applicantData.rent,
        employment_verified: applicantData.employmentVerified || false,
        income_verified: applicantData.incomeVerified || false,
        previous_evictions: applicantData.evictions || 0,
        rental_history_years: applicantData.rentalHistory || 0,
        on_time_payments_percent: applicantData.onTimePayments || 100,
        late_payments_count: applicantData.latePayments || 0,
        security_deposit: applicantData.deposit || 0,
        lease_term_months: applicantData.leaseTerm || 12,
        bedrooms: applicantData.bedrooms || 1,
        market_median_rent: applicantData.marketRent || 0,
        local_unemployment_rate: 5.0,
        inflation_rate: 3.0
      })
    });

    const result = await response.json();
    return result;
    
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
}

// Example usage in your component
const handleSubmit = async () => {
  const result = await scoreApplicant({
    id: "APL123",
    name: "John Doe",
    age: 30,
    income: 5000,
    creditScore: 720,
    rent: 1500,
    employmentVerified: true,
    // ... other fields
  });

  console.log("Risk Score:", result.risk_score);
  console.log("Recommendation:", result.recommendation);
  console.log("Reasoning:", result.reasoning);
};
```

---

## Step 3: Display Results in Lovable

```typescript
// In your Lovable component
function ApplicantResults({ score }) {
  return (
    <div className="results-card">
      <h2>Risk Assessment</h2>
      
      {/* Risk Score */}
      <div className="risk-score">
        <span className="score-value">{score.risk_score}%</span>
        <span className="score-label">Default Risk</span>
      </div>
      
      {/* Risk Category Badge */}
      <div className={`badge ${score.risk_category.toLowerCase()}`}>
        {score.risk_category} RISK
      </div>
      
      {/* Recommendation */}
      <div className="recommendation">
        <h3>{score.recommendation}</h3>
        <p>{score.reasoning}</p>
      </div>
      
      {/* Confidence */}
      <div className="confidence">
        Model Confidence: {(score.confidence * 100).toFixed(1)}%
      </div>
    </div>
  );
}
```

---

## Step 4: Styling (Optional CSS)

```css
.results-card {
  padding: 20px;
  border-radius: 8px;
  background: white;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.risk-score {
  text-align: center;
  margin: 20px 0;
}

.score-value {
  font-size: 48px;
  font-weight: bold;
  color: #333;
}

.badge {
  display: inline-block;
  padding: 8px 16px;
  border-radius: 20px;
  font-weight: bold;
  text-transform: uppercase;
}

.badge.low {
  background: #10b981;
  color: white;
}

.badge.medium {
  background: #f59e0b;
  color: white;
}

.badge.high {
  background: #ef4444;
  color: white;
}

.recommendation h3 {
  color: #1f2937;
  margin-bottom: 8px;
}

.recommendation p {
  color: #6b7280;
  line-height: 1.6;
}
```

---

## Step 5: Testing the Connection

### Test with cURL (PowerShell):

```powershell
$body = @{
    applicant_id = "TEST001"
    name = "Test User"
    age = 30
    monthly_income = 5000
    credit_score = 720
    monthly_rent = 1500
    employment_verified = $true
    income_verified = $true
    previous_evictions = 0
    rental_history_years = 3
    on_time_payments_percent = 95
    late_payments_count = 1
    security_deposit = 1500
    lease_term_months = 12
    bedrooms = 2
    market_median_rent = 1600
    local_unemployment_rate = 4.5
    inflation_rate = 3.2
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/score" -Method Post -Body $body -ContentType "application/json"
```

Expected response:
```json
{
  "success": true,
  "applicant_id": "TEST001",
  "risk_score": 5,
  "risk_category": "LOW",
  "default_probability": 0.05,
  "recommendation": "APPROVE",
  "confidence": 0.90,
  "reasoning": "Low default risk (5.0%). Strong applicant profile."
}
```

---

## Step 6: Deploy to Production (Later)

When ready to deploy:

1. **Host API on cloud** (Railway, Render, AWS, etc.)
2. **Get public URL** (e.g., `https://your-api.railway.app`)
3. **Update Lovable** to use production URL:
   ```typescript
   const API_URL = "https://your-api.railway.app/api/score";
   ```
4. **Add API key authentication** (for security)

---

## Minimal Example - Complete Flow

```typescript
// Lovable Component
import { useState } from 'react';

export default function ApplicantScoring() {
  const [applicant, setApplicant] = useState({
    name: '',
    age: 18,
    income: 0,
    creditScore: 300,
    rent: 0
  });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleScore = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/score', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          applicant_id: `APL${Date.now()}`,
          name: applicant.name,
          age: applicant.age,
          monthly_income: applicant.income,
          credit_score: applicant.creditScore,
          monthly_rent: applicant.rent,
          employment_verified: true,
          income_verified: true,
          previous_evictions: 0,
          rental_history_years: 2,
          on_time_payments_percent: 90,
          late_payments_count: 2,
          security_deposit: applicant.rent,
          lease_term_months: 12,
          bedrooms: 1,
          market_median_rent: applicant.rent * 1.1,
          local_unemployment_rate: 5.0,
          inflation_rate: 3.0
        })
      });
      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error('Error:', error);
      alert('Failed to score applicant');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Tenant Risk Scoring</h1>
      
      <div className="space-y-4 mb-4">
        <input
          type="text"
          placeholder="Name"
          value={applicant.name}
          onChange={(e) => setApplicant({...applicant, name: e.target.value})}
          className="border p-2 rounded w-full"
        />
        
        <input
          type="number"
          placeholder="Age"
          value={applicant.age}
          onChange={(e) => setApplicant({...applicant, age: parseInt(e.target.value)})}
          className="border p-2 rounded w-full"
        />
        
        <input
          type="number"
          placeholder="Monthly Income"
          value={applicant.income}
          onChange={(e) => setApplicant({...applicant, income: parseFloat(e.target.value)})}
          className="border p-2 rounded w-full"
        />
        
        <input
          type="number"
          placeholder="Credit Score (300-850)"
          value={applicant.creditScore}
          onChange={(e) => setApplicant({...applicant, creditScore: parseInt(e.target.value)})}
          className="border p-2 rounded w-full"
        />
        
        <input
          type="number"
          placeholder="Monthly Rent"
          value={applicant.rent}
          onChange={(e) => setApplicant({...applicant, rent: parseFloat(e.target.value)})}
          className="border p-2 rounded w-full"
        />
        
        <button
          onClick={handleScore}
          disabled={loading}
          className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? 'Scoring...' : 'Score Applicant'}
        </button>
      </div>

      {result && (
        <div className="mt-6 p-4 border rounded bg-gray-50">
          <h2 className="text-xl font-bold mb-2">Results</h2>
          <div className="space-y-2">
            <p><strong>Risk Score:</strong> {result.risk_score}%</p>
            <p><strong>Category:</strong> {result.risk_category}</p>
            <p><strong>Recommendation:</strong> {result.recommendation}</p>
            <p><strong>Reasoning:</strong> {result.reasoning}</p>
            <p><strong>Confidence:</strong> {(result.confidence * 100).toFixed(1)}%</p>
          </div>
        </div>
      )}
    </div>
  );
}
```

---

## That's It! 

Three files total:
1. `honest_model.py` - Train model → creates `models/honest_model.pkl`
2. `simple_api.py` - FastAPI backend (this file)
3. Lovable dashboard - Frontend (copy code above)

**Start API** → **Call from Lovable** → **Display results** ✅
