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
        if price_diff >= 20:
            return {
                "level": "High Risk",
                "color": "#b91c1c",
                "bg": "#fee2e2",
                "icon": "AlertCircle",
                "title": "Flood Warning",
                "description": "Excess water may damage roots and increase disease risk.",
                "yield_impact": "Yield may decrease by 20–40%.",
                "price_impact": "Prices may increase due to reduced supply.",
                "percentage": 40,
                "recommendations": [
                    "Improve field drainage immediately",
                    "Avoid additional irrigation",
                    "Monitor plants for fungal diseases",
                    "Delay harvesting until water recedes",
                    "Check roots for root rot signs",
                ],
            }
        elif price_diff >= 0:
            return {
                "level": "Medium Risk",
                "color": "#f59e0b",
                "bg": "#fef3c7",
                "icon": "AlertTriangle",
                "title": "Flood Alert",
                "description": "Flood conditions are present but impact is moderate.",
                "yield_impact": "Yield may decrease by 10–20%.",
                "price_impact": "Prices may rise moderately as supply is affected.",
                "percentage": 20,
                "recommendations": [
                    "Check drainage channels and remove blockages",
                    "Protect young plants from standing water",
                    "Reduce fertilizer applications until fields dry",
                    "Monitor weather updates closely",
                ],
            }
        else:
            return {
                "level": "Low Risk",
                "color": "#047857",
                "bg": "#d1fae5",
                "icon": "CheckCircle",
                "title": "Flood Condition Under Control",
                "description": "Flood risk is low and conditions are manageable.",
                "yield_impact": "Minimal yield impact expected.",
                "price_impact": "Prices are likely to remain stable.",
                "percentage": 10,
                "recommendations": [
                    "Keep drainage clear and inspect the field",
                    "Continue normal irrigation once waters recede",
                    "Watch for early signs of disease",
                    "Prepare for further weather changes",
                ],
            }
    elif disaster == "Drought":
        if price_diff >= 10:
            return {
                "level": "High Risk",
                "color": "#b91c1c",
                "bg": "#fee2e2",
                "icon": "AlertCircle",
                "title": "Drought Warning",
                "description": "Low rainfall and high temperatures are stressing crops.",
                "yield_impact": "Yield may decrease by 20–40%.",
                "price_impact": "Prices may increase due to reduced supply.",
                "percentage": 40,
                "recommendations": [
                    "Implement drip irrigation to conserve water",
                    "Apply mulch to retain soil moisture",
                    "Monitor plants daily for stress signs",
                    "Harvest early if plant health declines",
                    "Consider shade farming techniques",
                ],
            }
        elif price_diff >= 0:
            return {
                "level": "Medium Risk",
                "color": "#f59e0b",
                "bg": "#fef3c7",
                "icon": "AlertTriangle",
                "title": "Drought Alert",
                "description": "Drought is developing and crop stress is moderate.",
                "yield_impact": "Yield may decrease by 10–20%.",
                "price_impact": "Prices may rise as supply tightens.",
                "percentage": 20,
                "recommendations": [
                    "Increase soil moisture monitoring",
                    "Use mulch and shade to reduce evaporation",
                    "Schedule irrigation for peak heat times",
                    "Inspect plants for early stress symptoms",
                ],
            }
        else:
            return {
                "level": "Low Risk",
                "color": "#047857",
                "bg": "#d1fae5",
                "icon": "CheckCircle",
                "title": "Drought Conditions Mild",
                "description": "Drought is present but impacts are currently low.",
                "yield_impact": "Yield may be slightly reduced.",
                "price_impact": "Prices are likely to stay close to normal.",
                "percentage": 10,
                "recommendations": [
                    "Maintain efficient irrigation practices",
                    "Use mulch or cover crops to preserve moisture",
                    "Monitor soil moisture regularly",
                    "Plan for targeted watering during hot periods",
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
                "percentage": 30,
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
                "percentage": 15,
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
                "percentage": 5,
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