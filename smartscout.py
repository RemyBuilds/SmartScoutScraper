from pydantic import BaseModel
import pandas as pd
import requests
import os

class Seller(BaseModel):
    sellerName: str
    amazonSellerId: str
    brandName: str
    monthlyRevenue: float = 0.0  # Default to 0 if missing/null
    estimateBrandPercentage: float = 0.0

# API configuration
url = "https://smartscoutapi-east.azurewebsites.net/api/brandcoverage/search"
headers = {
    "Accept": "text/plain",
    "Accept-Language": "en-US,en;q=0.9",
    "Authorization": f"{token goes here}",  # Keep your full token
    "Connection": "keep-alive",
    "Content-Type": "application/json-patch+json",
    "Origin": "https://app.smartscout.com",
    "Referer": "https://app.smartscout.com/",
    "Request-Id": "insert request ID",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "cross-site",
    "Sec-GPC": "1",
    "User-Agent": "User agent",
    "X-SmartScout-Marketplace": "US",
    "sec-ch-ua": '"Not(A:Brand";v="99", "Brave";v="133", "Chromium";v="133"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "traceparent": ""
}


payload = {"brandId": {brandID from network inspection} }

# Make the API request

try:
    response = requests.post(
        url=url,
        headers=headers,
        json=payload  # This sends the payload as JSON
    )
    response.raise_for_status()  # Check for HTTP errors
    data = response.json()  # Parse JSON response
except Exception as e:
    print(f"Request failed: {e}")
    exit()

# ========== PROCESS RESPONSE DATA ==========
try:
    payload_data = data["payload"]  # Now properly defined from response
    sellers = []
    for item in payload_data:
        # Validate required fields exist
        if not all(key in item for key in ["sellerName", "amazonSellerId", "brandName"]):
            print(f"Skipping invalid item: {item}")
            continue

        sellers.append(
            Seller(
                sellerName=item["sellerName"],
                amazonSellerId=item["amazonSellerId"],
                brandName=item["brandName"],
                monthlyRevenue=item.get("monthlyRevenue") or 0.0,
                estimateBrandPercentage=item.get("estimateBrandPercentage") or 0.0
            )
        )
except KeyError as e:
    print(f"Missing expected key in response: {e}")
    exit()

# ========== EXPORT TO EXCEL ==========
new_data = pd.DataFrame([seller.dict() for seller in sellers])
output_file = "sellers.xlsx"

if os.path.exists(output_file):
    existing_data = pd.read_excel(output_file)
    combined_data = pd.concat([existing_data, new_data], ignore_index=True)
else:
    combined_data = new_data

combined_data.to_excel(output_file, index=False)
print(f"Data appended. Total records: {len(new_data)}")
