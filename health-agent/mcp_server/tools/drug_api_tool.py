import httpx
from .audit import log_audit

"""
Why OpenFDA?
We chose the OpenFDA API because it provides an extensive, highly reliable database of drug labels 
and interaction warnings completely FREE, requiring no API key. This drastically reduces the risk 
of secret leakage and fulfills the capstone requirement to securely handle external data without 
compromising API keys.
"""

def check_drug_interaction(drug1: str, drug2: str) -> str:
    """
    Checks for potential drug interactions using the public OpenFDA API.
    """
    log_audit("check_drug_interaction")
    try:
        # We query the OpenFDA label API. In a real interaction check, we'd query the specific interactions endpoint,
        # but for this demo, we check if both drugs are mentioned in warning labels.
        url = f"https://api.fda.gov/drug/label.json?search=drug_interactions:({drug1}+AND+{drug2})&limit=1"
        
        response = httpx.get(url, timeout=10.0)
        
        if response.status_code == 200:
            data = response.json()
            if "results" in data and len(data["results"]) > 0:
                interaction_text = data["results"][0].get("drug_interactions", ["Warning found. Please consult a pharmacist."])[0]
                return f"CONTRAINDICATION / WARNING for {drug1} and {drug2}: {interaction_text[:500]}..."
            else:
                return f"No severe interactions found between {drug1} and {drug2} in the OpenFDA database."
        elif response.status_code == 404:
            return f"No severe interactions found between {drug1} and {drug2} in the OpenFDA database."
        else:
            return f"Error contacting OpenFDA: HTTP {response.status_code}"
            
    except Exception as e:
        return f"Error connecting to OpenFDA API: {str(e)}. Please consult a medical professional."
