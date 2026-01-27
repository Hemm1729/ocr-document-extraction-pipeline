import requests
import logging

def lookup_vin(vin):
    """
    Look up VIN details using the NHTSA API.
    """
    if not vin or len(vin) != 17:
        logging.warning(f"Invalid VIN format: {vin}")
        return {"error": "Invalid VIN length"}
        
    url = f"https://vpic.nhtsa.dot.gov/api/vehicles/decodevin/{vin}?format=json"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        results = data.get("Results", [])
        decoded = {}
        
        # Helper to find value by Variable key
        def get_val(key):
            for item in results:
                if item.get("Variable") == key:
                    return item.get("Value")
            return None

        decoded["Make"] = get_val("Make")
        decoded["Model"] = get_val("Model")
        decoded["Year"] = get_val("Model Year")
        decoded["Vehicle Type"] = get_val("Vehicle Type")
        decoded["Manufacturer"] = get_val("Manufacturer Name")
        
        return decoded

    except Exception as e:
        logging.error(f"VIN Lookup failed: {e}")
        return {"error": str(e)}
