from fastapi import APIRouter
from app.Utils.db import data_collection
from motor.motor_asyncio import AsyncIOMotorCursor

router = APIRouter()

def get_risk_level_and_info(disaster: str, price_diff: float) -> dict:
    """
    Rule-based risk analysis.
    Returns risk level, icon, color, title, description, recommendations.
    """
    if disaster == "Flood":
        return {
            "level": "High Risk",
            "color": "#1d4ed8",
            "bg": "#dbeafe",
            "icon": "AlertCircle",
            "title": "Flood Warning",
            "description": "Excess water may damage roots and increase disease risk.",
            "yield_impact": "Yield may decrease by 20–40%.",
            "price_impact": "Prices may increase due to reduced supply.",
            "recommendations": [
                "Improve field drainage immediately",
                "Avoid additional irrigation",
                "Monitor plants for fungal diseases",
                "Delay harvesting until water recedes",
                "Check roots for root rot signs",
            ],
        }
    elif disaster == "Drought":
        return {
            "level": "Medium Risk",
            "color": "#c2410c",
            "bg": "#fed7aa",
            "icon": "AlertTriangle",
            "title": "Drought Detected",
            "description": "Low rainfall and high temperatures may reduce crop yield.",
            "yield_impact": "Yield may decrease by 15–30%.",
            "price_impact": "Prices may increase due to reduced supply.",
            "recommendations": [
                "Implement drip irrigation to conserve water",
                "Apply mulch to retain soil moisture",
                "Monitor plants daily for stress signs",
                "Harvest early if plant health declines",
                "Consider shade farming techniques",
            ],
        }
    else:  # No disaster
        risk_desc = "Environmental conditions are stable for aloe cultivation."
        yield_msg = "No yield reduction expected."
        price_msg = "Prices remain stable."

        # Add price-based risk if applicable
        if price_diff < -20:
            return {
                "level": "High Risk (Price Drop)",
                "color": "#991b1b",
                "bg": "#fee2e2",
                "icon": "AlertCircle",
                "title": "Price Volatility Alert",
                "description": "Web price significantly lower than farm gate price.",
                "yield_impact": "No immediate yield impact.",
                "price_impact": f"Web price {price_diff:.0f} LKR below farm gate price. Market demand may be low.",
                "recommendations": [
                    "Reduce direct market sales to wholesale",
                    "Delay harvest to wait for better rates",
                    "Explore alternative buyer networks",
                    "Focus on quality to command premium prices",
                ],
            }
        elif price_diff < 0:
            return {
                "level": "Medium Risk (Price Gap)",
                "color": "#c2410c",
                "bg": "#fed7aa",
                "icon": "AlertTriangle",
                "title": "Price Gap Detected",
                "description": "Web price is lower than farm gate price.",
                "yield_impact": yield_msg,
                "price_impact": f"Web price {price_diff:.0f} LKR below farm gate. Margins are thin.",
                "recommendations": [
                    "Monitor market trends closely",
                    "Negotiate with buyers for better rates",
                    "Maintain good crop quality",
                    "Keep production costs optimized",
                ],
            }
        else:
            return {
                "level": "Low Risk",
                "color": "#15803d",
                "bg": "#dcfce7",
                "icon": "CheckCircle",
                "title": "Normal Conditions",
                "description": risk_desc,
                "yield_impact": yield_msg,
                "price_impact": price_msg,
                "recommendations": [
                    "Continue standard irrigation practices",
                    "Monitor soil moisture weekly",
                    "Maintain nutrient balance",
                    "Plan harvest timing to maximize profit",
                ],
            }


@router.get("/risk-analysis")
async def risk_analysis():
    """
    Comprehensive rule-based risk analysis.
    Fetches latest record and returns:
    - Latest data
    - Risk level, recommendations, actions, and impact info
    """
    # Fetch the latest record
    latest = await data_collection.find_one({}, sort=[("createdAt", -1)])

    if not latest:
        return {
            "error": "No production records found",
            "latest": None,
            "risk": None,
        }

    date = latest.get("date")
    qty = latest.get("productionQuantity", 0)
    cost = latest.get("totalCost", 0)
    farmer_price = latest.get("farmerPrice", 0)
    web_price = latest.get("webPrice", 0)
    disaster = latest.get("naturalDisaster", "No disaster")

    price_diff = web_price - farmer_price

    # Get risk info using rule engine
    risk_info = get_risk_level_and_info(disaster, price_diff)

    return {
        "latest": {
            "date": date,
            "productionQuantity": qty,
            "totalCost": cost,
            "farmerPrice": farmer_price,
            "webPrice": web_price,
            "naturalDisaster": disaster,
            "priceDifference": round(price_diff, 2),
        },
        "risk": risk_info,
    }
