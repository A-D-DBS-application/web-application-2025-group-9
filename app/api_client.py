import requests
from flask import current_app
from datetime import datetime

def get_company_details(clean_vat, api_key):
    """Fetch company details from bizzy.ai Details API"""
    url = f"https://api.bizzy.ai/v1/companies/BE/{clean_vat}"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json"
    }
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    return response.json()


def get_company_financials(vat_number):
    """Fetch comprehensive company data from bizzy.ai API (Details + Financials)"""
    api_key = current_app.config.get('BIZZY_API_KEY')
    if not api_key:
        raise ValueError("BIZZY_API_KEY not configured")
    
    # Clean VAT number: remove "BE", spaces, dots
    clean_vat = vat_number.replace("BE", "").replace(" ", "").replace(".", "")
    
    # Call Details endpoint
    details_data = get_company_details(clean_vat, api_key)
    
    # Call Financials endpoint
    financials_url = f"https://api.bizzy.ai/v1/companies/BE/{clean_vat}/financials"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json"
    }
    
    financials_response = requests.get(financials_url, headers=headers)
    financials_response.raise_for_status()
    financials_data = financials_response.json()
    
    # Extract company info from Details endpoint
    details = details_data.get("data", {})
    identifier = details_data.get("identifier", {})
    company_name = identifier.get("name")
    
    # Extract address
    address = details.get("address", {})
    street = address.get("street", "")
    number = address.get("number", "")
    box_val = address.get("box", "")
    postal = address.get("postalCode", "")
    place = address.get("place", "")
    
    # Build address: "Street Number, Box, Postal, Place"
    address_parts = []
    if street and number:
        address_parts.append(f"{street} {number}")  # No comma between street and number
    elif street:
        address_parts.append(street)
    
    if box_val and box_val != "//":
        address_parts.append(box_val)
    if postal:
        address_parts.append(postal)
    if place:
        address_parts.append(place)
    
    company_address_full = ", ".join(address_parts)
    
    # Parse established date
    established_since = None
    if details.get("establishedSince"):
        try:
            established_since = datetime.fromisoformat(details["establishedSince"].replace("Z", ""))
        except:
            pass
    
    # Get most recent financial data
    accounts = financials_data.get("data", [])
    if not accounts:
        raise ValueError("No financial data available")
    
    latest_account = max(accounts, key=lambda x: x.get("startDate", ""))
    
    # Extract financial metrics
    profitability = latest_account.get("profitability", {})
    liquidity = latest_account.get("liquidity", {})
    solvency = latest_account.get("solvency", {})
    
    # Calculate ratios
    total_assets = solvency.get("totalAssets")
    equity = solvency.get("equity")
    debt = solvency.get("debt")
    
    solvency_ratio = None
    debt_ratio = None
    
    if total_assets and total_assets > 0:
        if equity:
            solvency_ratio = (equity / total_assets) * 100
        if debt:
            debt_ratio = (debt / total_assets) * 100
    
    # Map to our Company model fields
    company_data = {
        "company_name": company_name,
        "vat_number": f"BE{clean_vat}",
        "company_address": company_address_full,
        "legal_status": details.get("legalStatus"),
        "established_since": established_since,
        "revenue_estimation": details.get("revenueEstimations"),
        "employee_estimation": details.get("employeeEstimations"),
        "common_score": details.get("commonScore"),
        "credit_limit": details.get("creditLimit"),
        "credit_score": latest_account.get("healthIndicator"),
        "solvency_ratio": round(solvency_ratio, 2) if solvency_ratio else None,
        "debt_ratio": round(debt_ratio, 2) if debt_ratio else None,
        "current_ratio": liquidity.get("currentRatio"),
        "quick_ratio": liquidity.get("quickRatio"),
        "cash": liquidity.get("cash"),  # Cash and cash equivalents
        "ebitda": profitability.get("ebitda"),
        "net_profit": profitability.get("netProfit"),
        "total_assets": total_assets,
        "equity": equity,
        "total_debt": debt,
        "sector": None  # Can be derived from NACE codes if needed
    }
    
    return company_data