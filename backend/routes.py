"""
API Routes — All endpoint definitions for Measles AI Sentinel
"""

import math
import base64
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List
from backend.gemini_service import (
    analyze_outbreak_risk,
    analyze_symptoms,
    analyze_rash_image,
    get_medical_guidance,
    generate_outbreak_alert,
)

router = APIRouter()


# ─── REQUEST MODELS ───────────────────────────────────────────────────────────

class RiskPredictionRequest(BaseModel):
    vaccination_rate: float = Field(..., ge=0, le=100, description="Vaccination rate in %")
    population_density: float = Field(..., gt=0, description="People per km²")
    recent_cases: int = Field(..., ge=0, description="Cases in last 30 days")
    season: str = Field(..., description="Current season")
    region_type: str = Field(..., description="Urban/Suburban/Rural")
    travel_activity: str = Field(..., description="Travel intensity")

class SymptomRequest(BaseModel):
    symptoms: List[str] = Field(..., description="List of symptom IDs")
    duration: str = Field(..., description="Duration of symptoms")
    exposure_history: str = Field(..., description="Known exposure")
    age_group: str = Field(default="Adult (18-60)", description="Patient age group")
    vaccination_status: str = Field(default="Unknown", description="Vaccination history")

class MedicalGuidanceRequest(BaseModel):
    condition: str
    severity: str
    patient_context: str

class AlertRequest(BaseModel):
    region: str
    cases: int
    vaccination_rate: float


# ─── RISK SCORE CALCULATOR ────────────────────────────────────────────────────
def calculate_risk_score(vax: float, density: float, cases: int, season: str, travel: str) -> float:
    score = 0.0
    # Vaccination gap (higher gap = higher risk)
    score += (100 - vax) * 0.45
    # Population density
    if density > 2000: score += 22
    elif density > 1000: score += 16
    elif density > 500: score += 10
    else: score += 4
    # Recent cases
    score += min(cases * 1.8, 28)
    # Seasonal risk
    if "High" in season: score += 14
    elif "Medium" in season: score += 8
    else: score += 3
    # Travel
    if "International" in travel: score += 12
    elif "Regional" in travel: score += 6
    else: score += 2
    return round(min(score, 100), 1)


# ─── PROBABILITY CALCULATOR ───────────────────────────────────────────────────
SYMPTOM_WEIGHTS = {
    "fever": 20, "rash": 28, "cough": 15, "red_eyes": 15,
    "koplik": 30, "runny_nose": 10, "fatigue": 8, "sensitivity": 12,
    "sore_throat": 7, "vomiting": 6, "body_pain": 7, "headache": 9
}

def calculate_symptom_probability(symptoms: list, exposure: str, duration: str) -> float:
    prob = sum(SYMPTOM_WEIGHTS.get(s, 5) for s in symptoms)
    if "Confirmed" in exposure: prob += 22
    elif "Possible" in exposure: prob += 12
    if "4-7" in duration: prob *= 1.12
    elif "More" in duration: prob *= 1.08
    return round(min(prob, 99), 1)


# ─── ENDPOINTS ────────────────────────────────────────────────────────────────

@router.get("/ping")
async def ping():
    return {"message": "Measles AI Sentinel API is running ✅"}


@router.post("/predict-risk")
async def predict_risk(req: RiskPredictionRequest):
    """
    Calculate outbreak risk score and generate AI-powered analysis via Gemini.
    """
    try:
        risk_score = calculate_risk_score(
            req.vaccination_rate, req.population_density,
            req.recent_cases, req.season, req.travel_activity
        )
        
        ai_analysis = await analyze_outbreak_risk(
            vaccination_rate=req.vaccination_rate,
            population_density=req.population_density,
            recent_cases=req.recent_cases,
            season=req.season,
            region_type=req.region_type,
            travel_activity=req.travel_activity,
            risk_score=risk_score
        )
        
        return JSONResponse({
            "success": True,
            "risk_score": risk_score,
            "vaccination_gap": round(100 - req.vaccination_rate, 1),
            "ai_analysis": ai_analysis
        })
    
    except ValueError as e:
        raise HTTPException(status_code=500, detail=f"Gemini API error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-symptoms")
async def analyze_symptoms_endpoint(req: SymptomRequest):
    """
    Analyze submitted symptoms and return measles probability + Gemini clinical guidance.
    """
    try:
        probability = calculate_symptom_probability(
            req.symptoms, req.exposure_history, req.duration
        )
        
        ai_result = await analyze_symptoms(
            symptoms=req.symptoms,
            duration=req.duration,
            exposure_history=req.exposure_history,
            age_group=req.age_group,
            vaccination_status=req.vaccination_status,
            probability=probability
        )
        
        return JSONResponse({
            "success": True,
            "probability": probability,
            "symptom_count": len(req.symptoms),
            "ai_analysis": ai_result
        })
    
    except ValueError as e:
        raise HTTPException(status_code=500, detail=f"Gemini API error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/scan-rash")
async def scan_rash(file: UploadFile = File(...)):
    """
    Upload rash image → Gemini Vision analyzes and classifies the rash.
    """
    try:
        # Validate file type
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image (JPG, PNG, WEBP)")
        
        # Read and encode image
        contents = await file.read()
        image_base64 = base64.b64encode(contents).decode("utf-8")
        
        ai_result = await analyze_rash_image(image_base64, file.content_type)
        
        return JSONResponse({
            "success": True,
            "filename": file.filename,
            "file_size_kb": round(len(contents) / 1024, 1),
            "ai_analysis": ai_result
        })
    
    except ValueError as e:
        raise HTTPException(status_code=500, detail=f"Gemini API error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/medical-guidance")
async def medical_guidance(req: MedicalGuidanceRequest):
    """
    Get AI-generated treatment protocol and medical guidance from Gemini.
    """
    try:
        result = await get_medical_guidance(req.condition, req.severity, req.patient_context)
        return JSONResponse({"success": True, "guidance": result})
    
    except ValueError as e:
        raise HTTPException(status_code=500, detail=f"Gemini API error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-alert")
async def generate_alert(req: AlertRequest):
    """
    Generate dynamic AI-powered outbreak alert message.
    """
    try:
        result = await generate_outbreak_alert(req.region, req.cases, req.vaccination_rate)
        return JSONResponse({"success": True, "alert": result})
    
    except ValueError as e:
        raise HTTPException(status_code=500, detail=f"Gemini API error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/regional-data")
async def get_regional_data():
    """
    Returns static regional outbreak and vaccination data for map/charts.
    """
    return JSONResponse({
        "regions": [
            {"name": "Downtown Metro", "lat": 40.7128, "lng": -74.006, "risk": "high", "cases": 45, "vaccination": 65, "risk_score": 78},
            {"name": "North District",  "lat": 40.7831, "lng": -73.9712, "risk": "medium", "cases": 18, "vaccination": 78, "risk_score": 52},
            {"name": "East Side",       "lat": 40.7282, "lng": -73.7949, "risk": "low",    "cases": 5,  "vaccination": 89, "risk_score": 18},
            {"name": "West End",        "lat": 40.6892, "lng": -74.1745, "risk": "medium", "cases": 22, "vaccination": 72, "risk_score": 55},
            {"name": "South Bay",       "lat": 40.5795, "lng": -74.1502, "risk": "high",   "cases": 38, "vaccination": 61, "risk_score": 81},
            {"name": "Riverside Zone",  "lat": 40.8448, "lng": -73.8648, "risk": "low",    "cases": 3,  "vaccination": 92, "risk_score": 12},
        ],
        "overall_coverage": 76.0,
        "target_coverage": 95.0,
        "total_cases": 131,
        "trend": [
            {"month": "Jan", "coverage": 72, "cases": 38},
            {"month": "Feb", "coverage": 74, "cases": 35},
            {"month": "Mar", "coverage": 74, "cases": 31},
            {"month": "Apr", "coverage": 75, "cases": 28},
            {"month": "May", "coverage": 76, "cases": 25},
        ]
    })
