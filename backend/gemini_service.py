"""
Gemini AI Service — Handles all AI/ML interactions via Google Gemini API
"""

import os
import base64
import json
from typing import Optional
import google.generativeai as genai
from PIL import Image
import io

# ─── Configure Gemini ────────────────────────────────────────────────────────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def get_model(vision: bool = False):
    """Return configured Gemini model instance."""
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not set. Add it to your .env file.")
    genai.configure(api_key=GEMINI_API_KEY)
    # gemini-2.0-flash handles both text and vision
    return genai.GenerativeModel("gemini-2.0-flash")


# ─── SYSTEM CONTEXT ──────────────────────────────────────────────────────────
MEDICAL_SYSTEM_CONTEXT = """You are an expert AI medical intelligence system specializing in 
infectious disease epidemiology, specifically measles outbreak detection and prevention. 
You provide evidence-based, clinically accurate guidance while always reminding users to 
consult healthcare professionals. Your responses are concise, structured, and actionable.
Always include a disclaimer that this is informational only."""


# ─── 1. RISK PREDICTION ──────────────────────────────────────────────────────
async def analyze_outbreak_risk(
    vaccination_rate: float,
    population_density: float,
    recent_cases: int,
    season: str,
    region_type: str,
    travel_activity: str,
    risk_score: float
) -> dict:
    """Generate AI-powered outbreak risk analysis using Gemini."""
    
    prompt = f"""
{MEDICAL_SYSTEM_CONTEXT}

Analyze this measles outbreak risk scenario and return a JSON response:

INPUT PARAMETERS:
- Vaccination Rate: {vaccination_rate}%
- Population Density: {population_density} people/km²
- Recent Cases (30 days): {recent_cases}
- Season: {season}
- Region Type: {region_type}
- Travel Activity: {travel_activity}
- Calculated Risk Score: {risk_score}/100

Return ONLY a valid JSON object (no markdown, no extra text) with this exact structure:
{{
  "risk_level": "LOW" | "MODERATE" | "HIGH" | "CRITICAL",
  "risk_score": {risk_score},
  "summary": "2-sentence summary of the outbreak risk situation",
  "primary_risk_factors": ["factor1", "factor2", "factor3"],
  "recommended_actions": ["action1", "action2", "action3", "action4"],
  "vaccination_gap_analysis": "1-2 sentences on the vaccination coverage gap",
  "seasonality_impact": "1 sentence on seasonal risk contribution",
  "herd_immunity_status": "ACHIEVED" | "AT_RISK" | "COMPROMISED",
  "estimated_r0_impact": "Brief explanation of transmission potential",
  "alert_level": "GREEN" | "YELLOW" | "ORANGE" | "RED",
  "time_to_outbreak": "Estimated timeframe if intervention not taken",
  "disclaimer": "Standard medical disclaimer"
}}
"""
    
    model = get_model()
    response = model.generate_content(prompt)
    text = response.text.strip()
    
    # Clean JSON from markdown if present
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()
    
    return json.loads(text)


# ─── 2. SYMPTOM ANALYSIS ─────────────────────────────────────────────────────
async def analyze_symptoms(
    symptoms: list[str],
    duration: str,
    exposure_history: str,
    age_group: str,
    vaccination_status: str,
    probability: float
) -> dict:
    """AI-powered symptom analysis and measles probability assessment."""
    
    symptoms_str = ", ".join(symptoms) if symptoms else "None reported"
    
    prompt = f"""
{MEDICAL_SYSTEM_CONTEXT}

Analyze these patient symptoms for measles probability and return a JSON response:

PATIENT DATA:
- Symptoms: {symptoms_str}
- Duration: {duration}
- Exposure History: {exposure_history}
- Age Group: {age_group}
- Vaccination Status: {vaccination_status}
- Calculated Measles Probability: {probability}%

Return ONLY a valid JSON object with this exact structure:
{{
  "measles_probability": {probability},
  "confidence_level": "LOW" | "MODERATE" | "HIGH",
  "clinical_assessment": "3-4 sentence clinical interpretation of the symptoms",
  "key_diagnostic_indicators": ["indicator1", "indicator2", "indicator3"],
  "differential_diagnoses": [
    {{"condition": "name", "probability": 0-100, "reasoning": "brief reason"}},
    {{"condition": "name", "probability": 0-100, "reasoning": "brief reason"}},
    {{"condition": "name", "probability": 0-100, "reasoning": "brief reason"}}
  ],
  "immediate_actions": ["action1", "action2", "action3"],
  "isolation_guidance": "Specific isolation recommendations",
  "when_to_seek_emergency_care": "Warning signs requiring immediate ER visit",
  "medication_guidance": "OTC medication guidance and what to avoid",
  "vitamin_guidance": "Vitamin A and nutritional recommendations",
  "contagion_risk": "LOW" | "MODERATE" | "HIGH",
  "incubation_note": "Incubation period context if relevant",
  "follow_up_recommendation": "When and where to follow up",
  "disclaimer": "Standard medical disclaimer"
}}
"""
    
    model = get_model()
    response = model.generate_content(prompt)
    text = response.text.strip()
    
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()
    
    return json.loads(text)


# ─── 3. RASH IMAGE ANALYSIS ──────────────────────────────────────────────────
async def analyze_rash_image(image_base64: str, media_type: str = "image/jpeg") -> dict:
    """Analyze rash image using Gemini Vision for measles classification."""
    
    model = get_model(vision=True)
    
    # Decode base64 to PIL Image
    image_bytes = base64.b64decode(image_base64)
    image = Image.open(io.BytesIO(image_bytes))
    
    prompt = f"""
{MEDICAL_SYSTEM_CONTEXT}

You are analyzing a medical rash image for diagnostic classification. 
Examine the visual characteristics carefully and return ONLY a valid JSON object:

{{
  "primary_classification": "Measles Rash" | "Chickenpox" | "Rubella" | "Roseola" | "Scarlet Fever" | "Drug Reaction" | "Contact Dermatitis" | "Other Viral Exanthem" | "Non-infectious Rash",
  "confidence_score": 0-100,
  "visual_features_observed": ["feature1", "feature2", "feature3", "feature4"],
  "rash_characteristics": {{
    "distribution": "description of rash distribution",
    "morphology": "macules/papules/vesicles/etc",
    "color": "color description",
    "pattern": "confluent/discrete/etc"
  }},
  "measles_likelihood": "UNLIKELY" | "POSSIBLE" | "PROBABLE" | "HIGHLY PROBABLE",
  "differential_diagnoses": [
    {{"condition": "name", "confidence": 0-100, "distinguishing_factors": "brief explanation"}},
    {{"condition": "name", "confidence": 0-100, "distinguishing_factors": "brief explanation"}},
    {{"condition": "name", "confidence": 0-100, "distinguishing_factors": "brief explanation"}}
  ],
  "clinical_correlation_needed": true | false,
  "urgent_care_recommended": true | false,
  "urgency_reason": "reason if urgent care recommended",
  "dermatological_assessment": "2-3 sentence clinical description of what is observed",
  "recommended_next_steps": ["step1", "step2", "step3"],
  "image_quality": "POOR" | "ADEQUATE" | "GOOD" | "EXCELLENT",
  "disclaimer": "This AI analysis is for informational purposes only and does not constitute medical diagnosis."
}}
"""
    
    response = model.generate_content([prompt, image])
    text = response.text.strip()
    
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()
    
    return json.loads(text)


# ─── 4. MEDICAL GUIDANCE ─────────────────────────────────────────────────────
async def get_medical_guidance(
    condition: str,
    severity: str,
    patient_context: str
) -> dict:
    """Get detailed medical guidance and treatment recommendations."""
    
    prompt = f"""
{MEDICAL_SYSTEM_CONTEXT}

Provide comprehensive medical guidance for the following case:

CONDITION: {condition}
SEVERITY: {severity}
PATIENT CONTEXT: {patient_context}

Return ONLY a valid JSON object:
{{
  "condition_overview": "2-3 sentence overview of the condition",
  "treatment_protocol": {{
    "immediate_care": ["step1", "step2", "step3"],
    "medications": [
      {{"name": "med name", "purpose": "what it treats", "note": "important note"}},
      {{"name": "med name", "purpose": "what it treats", "note": "important note"}}
    ],
    "supportive_care": ["care1", "care2", "care3"],
    "vitamin_a_protocol": "Vitamin A dosing guidance as per WHO"
  }},
  "isolation_protocol": {{
    "duration": "isolation duration",
    "precautions": ["precaution1", "precaution2"],
    "return_to_normal": "criteria for ending isolation"
  }},
  "monitoring": {{
    "watch_for": ["symptom1", "symptom2", "symptom3"],
    "red_flags": ["flag1", "flag2"],
    "follow_up_timeline": "when to follow up"
  }},
  "prevention_for_contacts": ["measure1", "measure2", "measure3"],
  "public_health_reporting": "guidance on reporting to health authorities",
  "prognosis": "Expected recovery timeline and outcomes",
  "disclaimer": "Medical disclaimer"
}}
"""
    
    model = get_model()
    response = model.generate_content(prompt)
    text = response.text.strip()
    
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()
    
    return json.loads(text)


# ─── 5. OUTBREAK ALERTS ──────────────────────────────────────────────────────
async def generate_outbreak_alert(region: str, cases: int, vaccination_rate: float) -> dict:
    """Generate dynamic outbreak alert message."""
    
    prompt = f"""
{MEDICAL_SYSTEM_CONTEXT}

Generate an outbreak alert for this situation:
- Region: {region}
- Active Cases: {cases}
- Vaccination Rate: {vaccination_rate}%

Return ONLY a valid JSON object:
{{
  "alert_title": "short alert title",
  "alert_message": "2-sentence urgent public health message",
  "severity": "WARNING" | "ALERT" | "CRITICAL",
  "recommended_response": ["response1", "response2", "response3"],
  "public_advisory": "1-sentence public advisory message"
}}
"""
    
    model = get_model()
    response = model.generate_content(prompt)
    text = response.text.strip()
    
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()
    
    return json.loads(text)
