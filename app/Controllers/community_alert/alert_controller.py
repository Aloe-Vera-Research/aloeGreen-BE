from fastapi import APIRouter, HTTPException
from app.Model.community_alert.alert_schema import EmailAlertRequest
from app.Utils.email_sender import send_disease_alert_email

router = APIRouter(prefix="/community-alert", tags=["Community Alert"])


@router.post("/send-email")
async def send_email_alert(payload: EmailAlertRequest):
    try:
        if payload.severity.lower() not in ["high", "critical"]:
            raise HTTPException(
                status_code=400,
                detail="Email alerts are only allowed for high or critical severity diseases."
            )

        send_disease_alert_email(
            disease=payload.disease,
            severity=payload.severity,
            spread_risk=payload.spread_risk,
            message=payload.message,
            latitude=payload.latitude,
            longitude=payload.longitude,
        )

        return {"message": "Alert email sent successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))