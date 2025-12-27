/**
 * Leaseth Frontend JavaScript
 * Handles form submission, API calls, and result display
 */

const API_BASE_URL = "http://localhost:8000/api/v1";

/**
 * Collect form data and convert to JSON
 */
function getFormData() {
    return {
        applicant_id: document.getElementById('applicant_id').value,
        name: document.getElementById('name').value,
        age: parseInt(document.getElementById('age').value),
        employment_status: document.getElementById('employment_status').value,
        employment_verified: document.getElementById('employment_verified').checked,
        income_verified: document.getElementById('income_verified').checked,
        monthly_income: parseFloat(document.getElementById('monthly_income').value),
        credit_score: parseInt(document.getElementById('credit_score').value),
        previous_evictions: parseInt(document.getElementById('previous_evictions').value),
        rental_history_years: parseFloat(document.getElementById('rental_history_years').value),
        on_time_payments_percent: parseFloat(document.getElementById('on_time_payments_percent').value),
        late_payments_count: parseInt(document.getElementById('late_payments_count').value),
        monthly_rent: parseFloat(document.getElementById('monthly_rent').value),
        security_deposit: parseFloat(document.getElementById('security_deposit').value),
        lease_term_months: parseInt(document.getElementById('lease_term_months').value),
        bedrooms: parseInt(document.getElementById('bedrooms').value),
        property_type: document.getElementById('property_type').value,
        location: document.getElementById('location').value,
        market_median_rent: parseFloat(document.getElementById('market_median_rent').value),
        local_unemployment_rate: parseFloat(document.getElementById('local_unemployment_rate').value),
        inflation_rate: parseFloat(document.getElementById('inflation_rate').value)
    };
}

/**
 * Validate form data
 */
function validateFormData(data) {
    const errors = [];

    if (!data.applicant_id) errors.push("Applicant ID is required");
    if (!data.name) errors.push("Name is required");
    if (data.age < 18 || data.age > 120) errors.push("Age must be between 18 and 120");
    if (!data.employment_status) errors.push("Employment status is required");
    if (data.monthly_income <= 0) errors.push("Monthly income must be positive");
    if (data.credit_score < 300 || data.credit_score > 850) errors.push("Credit score must be 300-850");
    if (data.rental_history_years < 0) errors.push("Rental history cannot be negative");
    if (data.monthly_rent <= 0) errors.push("Monthly rent must be positive");
    if (data.monthly_rent > data.monthly_income * 2) errors.push("Rent cannot exceed 2x monthly income");

    return errors;
}

/**
 * Calculate risk score
 */
async function calculateScore() {
    try {
        // Get form data
        const formData = getFormData();

        // Validate form data
        const errors = validateFormData(formData);
        if (errors.length > 0) {
            alert("Form Validation Errors:\n" + errors.join("\n"));
            return;
        }

        // Show loading state
        const btn = event.target;
        btn.disabled = true;
        btn.textContent = "Calculating...";

        // Call API
        const response = await fetch(`${API_BASE_URL}/score`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer test_key'  // For MVP testing
            },
            body: JSON.stringify(formData)
        });

        const result = await response.json();

        // Restore button
        btn.disabled = false;
        btn.textContent = "Calculate Risk Score";

        if (!response.ok) {
            alert(`API Error: ${result.error || 'Unknown error'}`);
            return;
        }

        // Display results
        displayResults(result.data);

    } catch (error) {
        console.error('Error:', error);
        alert(`Error: ${error.message}`);
        event.target.disabled = false;
        event.target.textContent = "Calculate Risk Score";
    }
}

/**
 * Display results on the page
 */
function displayResults(data) {
    // Update risk score and category
    document.getElementById('riskScore').textContent = `${data.risk_score}%`;
    
    const categoryClass = `status-${data.risk_category.toLowerCase()}`;
    document.getElementById('riskCategory').textContent = data.risk_category;
    document.getElementById('riskCategory').className = `result-value ${categoryClass}`;

    // Update recommendation
    document.getElementById('recommendation').textContent = data.recommendation;
    document.getElementById('recommendation').className = `result-value status-${getRiskStatus(data.risk_score)}`;

    // Update confidence and probability
    document.getElementById('confidence').textContent = `${(data.confidence_score * 100).toFixed(1)}%`;
    document.getElementById('probability').textContent = `${(data.default_probability * 100).toFixed(2)}%`;

    // Display full JSON response
    document.getElementById('jsonResponse').textContent = JSON.stringify(data, null, 2);

    // Draw risk gauge
    drawRiskGauge(data.risk_score);

    // Show results section
    document.getElementById('resultsSection').style.display = 'block';
    document.getElementById('resultsSection').scrollIntoView({ behavior: 'smooth' });
}

/**
 * Get risk status string
 */
function getRiskStatus(riskScore) {
    if (riskScore < 30) return 'low';
    if (riskScore < 60) return 'medium';
    return 'high';
}

/**
 * Draw SVG risk gauge
 */
function drawRiskGauge(riskScore) {
    const svg = document.getElementById('riskGauge');
    svg.innerHTML = '';

    const width = 200;
    const height = 120;
    const radius = 80;
    const centerX = width / 2;
    const centerY = height - 10;

    // Determine color
    let color;
    if (riskScore < 30) color = '#28a745';  // Low - Green
    else if (riskScore < 60) color = '#ffc107';  // Medium - Yellow
    else color = '#dc3545';  // High - Red

    // Draw background arc
    const bgPath = describeArc(centerX, centerY, radius, 180, 0);
    const bgArc = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    bgArc.setAttribute('d', bgPath);
    bgArc.setAttribute('stroke', '#e9ecef');
    bgArc.setAttribute('stroke-width', '10');
    bgArc.setAttribute('fill', 'none');
    svg.appendChild(bgArc);

    // Draw risk arc
    const angle = 180 - (riskScore / 100) * 180;
    const riskPath = describeArc(centerX, centerY, radius, 180, angle);
    const riskArc = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    riskArc.setAttribute('d', riskPath);
    riskArc.setAttribute('stroke', color);
    riskArc.setAttribute('stroke-width', '10');
    riskArc.setAttribute('fill', 'none');
    riskArc.setAttribute('stroke-linecap', 'round');
    svg.appendChild(riskArc);

    // Draw center circle
    const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    circle.setAttribute('cx', centerX);
    circle.setAttribute('cy', centerY);
    circle.setAttribute('r', '8');
    circle.setAttribute('fill', color);
    svg.appendChild(circle);
}

/**
 * Describe SVG arc
 */
function describeArc(x, y, radius, startAngle, endAngle) {
    const start = polarToCartesian(x, y, radius, endAngle);
    const end = polarToCartesian(x, y, radius, startAngle);
    const largeArc = endAngle - startAngle <= 180 ? "0" : "1";
    return [
        "M", start.x, start.y,
        "A", radius, radius, 0, largeArc, 0, end.x, end.y
    ].join(" ");
}

/**
 * Convert polar coordinates to Cartesian
 */
function polarToCartesian(centerX, centerY, radius, angleInDegrees) {
    const angleInRadians = (angleInDegrees - 90) * Math.PI / 180.0;
    return {
        x: centerX + (radius * Math.cos(angleInRadians)),
        y: centerY + (radius * Math.sin(angleInRadians))
    };
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('Leaseth Frontend Initialized');
    console.log('API Base URL:', API_BASE_URL);
});
