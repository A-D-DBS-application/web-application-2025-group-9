import requests
from flask import current_app

def get_company_financials(vat_number):
    """Fetch financial data from bizzy.ai API"""
    api_key = current_app.config.get('BIZZY_API_KEY')
    if not api_key:
        raise ValueError("BIZZY_API_KEY not configured")
    
    # Clean VAT number: remove "BE", spaces, dots
    clean_vat = vat_number.replace("BE", "").replace(" ", "").replace(".", "")
    
    url = f"https://api.bizzy.ai/v1/companies/BE/{clean_vat}/financials"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json"
    }
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raises exception for bad status
    
    # Parse JSON once into dict
    data = response.json()
    
    # Extract company info from identifier
    identifier = data.get("identifier", {})
    company_name = identifier.get("name")
    
    # Get most recent year's data
    accounts = data.get("data", [])
    if not accounts:
        raise ValueError("No financial data available")
    
    # Sort by year descending and take most recent
    latest_account = max(accounts, key=lambda x: x.get("startDate", ""))
    
    # Extract financial metrics
    profitability = latest_account.get("profitability", {})
    solvency = latest_account.get("solvency", {})
    
    # Map to our Company model fields
    company_data = {
        "company_name": company_name,
        "vat_number": f"BE{clean_vat}",  # Store in clean format: BE0473416418
        "credit_score": latest_account.get("healthIndicator"),  # This is the credit score
        "solvency_ratio": solvency.get("equity") / solvency.get("totalAssets") if solvency.get("totalAssets") else None,
        "debt_ratio": (solvency.get("debt") / solvency.get("totalAssets") * 100) if solvency.get("totalAssets") else None,
        "sector": None  # Not provided in API response
    }
    
    return company_data