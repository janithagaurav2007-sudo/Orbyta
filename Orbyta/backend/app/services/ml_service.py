from pathlib import Path
import joblib, numpy as np

MODEL_PATH=Path(__file__).resolve().parents[2]/"models"/"pcos_model.joblib"
FEATURES=["age","bmi","cycle_regular","cycle_length","missed_periods","acne","excess_hair","hair_thinning","weight_change","dark_skin","fatigue","stress","sleep","activity"]

def _fallback_probability(d):
    # Educational screening heuristic only; not clinically validated.
    score=0.08
    score += 0.16*(1-d["cycle_regular"])
    score += min(.22,.07*d["missed_periods"])
    score += .09*d["excess_hair"]+.07*d["acne"]+.07*d["hair_thinning"]
    score += .05*d["weight_change"]+.04*d["dark_skin"]+.03*d["fatigue"]
    score += .02*max(0,d["bmi"]-25)+.008*d["stress"]
    score -= .012*max(0,d["sleep"]-7)
    return float(max(.02,min(.95,score)))

def predict(data):
    if MODEL_PATH.exists():
        try:
            model=joblib.load(MODEL_PATH)
            x=np.array([[data[f] for f in FEATURES]],dtype=float)
            probability=float(model.predict_proba(x)[0][1]); source="trained ML model"
        except Exception:
            probability=_fallback_probability(data); source="local screening heuristic"
    else:
        probability=_fallback_probability(data); source="local screening heuristic"

    checks=[
      ("cycle_regular",data["cycle_regular"]==0,"Irregular or unpredictable cycles"),
      ("missed_periods",data["missed_periods"]>0,"Missed periods"),
      ("excess_hair",data["excess_hair"]==1,"Increased facial/body hair"),
      ("acne",data["acne"]==1,"Persistent acne"),
      ("hair_thinning",data["hair_thinning"]==1,"Scalp hair thinning"),
      ("weight_change",data["weight_change"]==1,"Recent weight change"),
      ("dark_skin",data["dark_skin"]==1,"Darkened skin in folds"),
      ("bmi",data["bmi"]>=25,"BMI in the higher range"),
      ("fatigue",data["fatigue"]==1,"Fatigue")
    ]
    factors=[label for _,yes,label in checks if yes][:6]
    if probability<.35: level="LOW"
    elif probability<.65: level="MODERATE"
    else: level="HIGH"

    risk_factors=[
      "Family history/genetic susceptibility can increase PCOS likelihood.",
      "Insulin resistance and metabolic factors are commonly associated with PCOS.",
      "PCOS is influenced by a combination of genetic, hormonal and metabolic factors; there is no single known cause."
    ]
    lifestyle=[
      "Aim for regular movement you can sustain, combining aerobic activity with strength work.",
      "Choose balanced meals with vegetables/fibre, protein and minimally processed carbohydrates; avoid crash diets.",
      "Prioritize consistent sleep and stress-management habits.",
      "If weight management is relevant to you, discuss a realistic plan with a clinician or dietitian rather than pursuing rapid weight loss."
    ]
    doctor=(probability>=.35 or data["missed_periods"]>=2 or data["cycle_length"]>=45 or data["excess_hair"] or data["hair_thinning"])
    return {"probability":round(probability,4),"percentage":round(probability*100,1),"level":level,
      "factors":factors,"risk_factors":risk_factors,"lifestyle":lifestyle,
      "doctor_check":doctor,
      "model_source":source,
      "disclaimer":"This is a screening estimate for awareness, not a diagnosis. PCOS diagnosis requires clinical assessment and may involve medical history, examination and/or tests."}
