from fastapi import FastAPI, Depends, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime
import hashlib, hmac, json, secrets, base64, os

from .database import Base, engine, get_db
from .models import User, ScreeningResult, CycleEntry, SymptomEntry, Checkin, Conversation
from .schemas import AuthIn, ProfileIn, SettingsIn, ScreeningInput, CycleIn, SymptomIn, CheckinIn, AmieIn
from .services.ml_service import predict
from .services.amie import reply

Base.metadata.create_all(bind=engine)
app = FastAPI(title="Orbyta API", version="2.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173","http://127.0.0.1:5173"],
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# Local-only signed session tokens. For production, replace with a real auth provider/JWT.
SECRET = os.getenv("ORBYTA_SECRET", "orbyta-local-development-secret-change-for-production")

def hash_password(password):
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 120000)
    return base64.b64encode(salt + digest).decode()

def verify_password(password, stored):
    try:
        raw = base64.b64decode(stored)
        salt, digest = raw[:16], raw[16:]
        check = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 120000)
        return hmac.compare_digest(digest, check)
    except Exception:
        return False

def token_for(user_id):
    raw = f"{user_id}:{SECRET}".encode()
    return base64.urlsafe_b64encode(raw).decode()

def user_from_header(db, x_user_token):
    if not x_user_token: raise HTTPException(401, "Please sign in to continue.")
    try:
        raw = base64.urlsafe_b64decode(x_user_token.encode()).decode()
        uid, secret = raw.split(":", 1)
        if not hmac.compare_digest(secret, SECRET): raise ValueError()
        user = db.query(User).filter(User.id == int(uid)).first()
        if not user: raise ValueError()
        return user
    except Exception:
        raise HTTPException(401, "Your session expired. Please sign in again.")

def current_user(db: Session = Depends(get_db), x_user_token: str = Header(default=None)):
    return user_from_header(db, x_user_token)

@app.get("/api/health")
def health(): return {"status":"ok","app":"Orbyta"}

@app.post("/api/auth/signup")
def signup(payload: AuthIn, db: Session=Depends(get_db)):
    email=payload.email.lower().strip()
    if db.query(User).filter(User.email==email).first(): raise HTTPException(409,"An account with this email already exists.")
    user=User(email=email,password_hash=hash_password(payload.password),name=(payload.name or "").strip(),amie_name="Amie",amie_avatar="bear",theme="light")
    db.add(user); db.commit(); db.refresh(user)
    return {"token":token_for(user.id),"user":{"id":user.id,"email":user.email,"name":user.name,"onboarding_complete":bool(user.name and user.age and user.height and user.weight)}}

@app.post("/api/auth/login")
def login(payload: AuthIn, db: Session=Depends(get_db)):
    user=db.query(User).filter(User.email==payload.email.lower().strip()).first()
    if not user or not verify_password(payload.password,user.password_hash): raise HTTPException(401,"Incorrect email or password.")
    return {"token":token_for(user.id),"user":{"id":user.id,"email":user.email,"name":user.name,"onboarding_complete":bool(user.name and user.age and user.height and user.weight)}}

@app.get("/api/me")
def me(user: User=Depends(current_user)):
    bmi=round(user.weight/((user.height/100)**2),1) if user.height and user.weight else None
    return {"id":user.id,"email":user.email,"name":user.name,"age":user.age,"height":user.height,"weight":user.weight,"bmi":bmi,"amie_name":user.amie_name,"amie_avatar":user.amie_avatar,"theme":user.theme,"onboarding_complete":bool(user.name and user.age and user.height and user.weight)}

@app.put("/api/profile")
def profile(payload: ProfileIn, db: Session=Depends(get_db), user: User=Depends(current_user)):
    user.name=payload.name.strip(); user.age=payload.age; user.height=payload.height; user.weight=payload.weight
    db.commit()
    return {"message":"Profile saved","bmi":round(user.weight/((user.height/100)**2),1)}

@app.put("/api/settings")
def settings(payload: SettingsIn, db: Session=Depends(get_db), user: User=Depends(current_user)):
    user.amie_name=payload.amie_name.strip() or "Amie"; user.amie_avatar=payload.amie_avatar; user.theme=payload.theme
    db.commit(); return {"message":"Settings saved","amie_name":user.amie_name,"amie_avatar":user.amie_avatar,"theme":user.theme}

def screening_for(db,user):
    return db.query(ScreeningResult).filter_by(user_id=user.id).order_by(desc(ScreeningResult.created_at)).first()

def dashboard_data(db,user):
    latest=screening_for(db,user)
    cycles=db.query(CycleEntry).filter_by(user_id=user.id).all()
    symptoms=db.query(SymptomEntry).filter_by(user_id=user.id).all()
    checkins=db.query(Checkin).filter_by(user_id=user.id).order_by(desc(Checkin.created_at)).limit(14).all()
    wellness=50
    if checkins:
        avg_sleep=sum(x.sleep for x in checkins)/len(checkins); avg_stress=sum(x.stress for x in checkins)/len(checkins)
        wellness=round(max(0,min(100,55+avg_sleep*4-avg_stress*2)))
    symptom_counts={}
    for s in symptoms: symptom_counts[s.symptom]=symptom_counts.get(s.symptom,0)+1
    screening_history_rows=db.query(ScreeningResult).filter_by(user_id=user.id).order_by(ScreeningResult.created_at).all()
    history=[{"id":r.id,"date":r.created_at.strftime("%b %d"),"probability":round(r.probability*100,1),"level":r.level} for r in screening_history_rows]
    return {"user":{"name":user.name,"age":user.age,"height":user.height,"weight":user.weight,
        "bmi":round(user.weight/((user.height/100)**2),1) if user.height and user.weight else None},
        "screening":None if not latest else {"level":latest.level,"percentage":round(latest.probability*100,1),"factors":json.loads(latest.factors or "[]"),
            "inputs":json.loads(latest.inputs or "{}"),"date":latest.created_at.strftime("%b %d")},
        "screening_history":history,
        "wellness":wellness,"cycle_count":len(cycles),"symptom_count":len(symptoms),
        "symptoms":[{"name":k,"value":v} for k,v in symptom_counts.items()],
        "checkins":[{"date":x.created_at.strftime("%b %d"),"mood":x.mood,"energy":x.energy,"stress":x.stress,"sleep":x.sleep} for x in reversed(checkins)]}

@app.post("/api/predict")
def make_prediction(payload: ScreeningInput, db: Session=Depends(get_db), user: User=Depends(current_user)):
    result=predict(payload.model_dump())
    row=ScreeningResult(user_id=user.id,probability=result["probability"],level=result["level"],factors=json.dumps(result["factors"]),inputs=json.dumps(payload.model_dump()))
    db.add(row); db.commit(); db.refresh(row); result["id"]=row.id
    return result

@app.get("/api/screening-history")
def screening_history(db: Session=Depends(get_db), user: User=Depends(current_user)):
    rows=db.query(ScreeningResult).filter_by(user_id=user.id).order_by(ScreeningResult.created_at).all()
    return [{"id":r.id,"date":r.created_at.strftime("%b %d"),"probability":round(r.probability*100,1),"level":r.level} for r in rows]

@app.get("/api/dashboard")
def dashboard(db: Session=Depends(get_db), user: User=Depends(current_user)): return dashboard_data(db,user)

@app.post("/api/cycle")
def add_cycle(payload: CycleIn, db: Session=Depends(get_db), user: User=Depends(current_user)):
    row=CycleEntry(user_id=user.id,**payload.model_dump()); db.add(row); db.commit(); return {"message":"Cycle entry saved","id":row.id}

@app.get("/api/cycle")
def get_cycles(db: Session=Depends(get_db), user: User=Depends(current_user)):
    rows=db.query(CycleEntry).filter_by(user_id=user.id).order_by(desc(CycleEntry.id)).all()
    return [{"id":r.id,"start_date":r.start_date,"end_date":r.end_date,"flow":r.flow,"cramps":r.cramps,"mood":r.mood,"energy":r.energy} for r in rows]

@app.post("/api/symptoms")
def add_symptom(payload: SymptomIn, db: Session=Depends(get_db), user: User=Depends(current_user)):
    row=SymptomEntry(user_id=user.id,**payload.model_dump()); db.add(row); db.commit(); return {"message":"Symptom saved","id":row.id}

@app.get("/api/symptoms")
def get_symptoms(db: Session=Depends(get_db), user: User=Depends(current_user)):
    rows=db.query(SymptomEntry).filter_by(user_id=user.id).order_by(desc(SymptomEntry.id)).all()
    return [{"id":r.id,"symptom":r.symptom,"severity":r.severity,"date":r.date} for r in rows]

@app.post("/api/checkin")
def add_checkin(payload: CheckinIn, db: Session=Depends(get_db), user: User=Depends(current_user)):
    row=Checkin(user_id=user.id,**payload.model_dump()); db.add(row); db.commit(); return {"message":"Check-in saved","id":row.id}

@app.get("/api/insights")
def insights(db: Session=Depends(get_db), user: User=Depends(current_user)):
    latest=screening_for(db,user); items=[]
    if latest:
        items.append(f"Your latest PCOS screening likelihood is {latest.probability*100:.1f}% ({latest.level.lower()}). This is a screening estimate, not a diagnosis.")
        if latest.probability>=.65: items.append("Because your screening pattern is elevated, consider discussing your symptoms and cycle history with a qualified clinician.")
        elif latest.probability>=.35: items.append("Several PCOS-associated features are present in your answers. Tracking changes and discussing persistent symptoms with a clinician may be useful.")
        else: items.append("Your current answers show fewer PCOS-associated features, but a low screening result does not rule out PCOS.")
    symptoms=db.query(SymptomEntry).filter_by(user_id=user.id).all()
    if symptoms:
        counts={}
        for s in symptoms: counts[s.symptom]=counts.get(s.symptom,0)+1
        top=max(counts,key=counts.get); items.append(f"{top} is the symptom you have logged most often.")
    if not items: items=["Complete a PCOS screening to unlock personalized risk factors, guidance and trend insights."]
    return {"insights":items}

@app.post("/api/amie")
def amie(payload: AmieIn, db: Session=Depends(get_db), user: User=Depends(current_user)):
    context=dashboard_data(db,user); answer=reply(payload.message,context)
    row=Conversation(user_id=user.id,message=payload.message,reply=answer); db.add(row); db.commit()
    return {"reply":answer}

@app.get("/api/report")
def report(db: Session=Depends(get_db), user: User=Depends(current_user)):
    return {"dashboard":dashboard_data(db,user),"screening_history":screening_history(db,user),
        "cycles":get_cycles(db,user),"symptoms":get_symptoms(db,user),
        "disclaimer":"Orbyta provides screening/awareness support and is not a medical diagnosis. A clinician is needed to diagnose PCOS."}

@app.get("/api/resources")
def resources():
    return {"resources":[
      {"id":"pcos","title":"PCOS: what it is","description":"WHO overview of PCOS, symptoms, diagnosis and management.","icon":"🌸","url":"https://www.who.int/news-room/fact-sheets/detail/polycystic-ovary-syndrome"},
      {"id":"guideline","title":"PCOS guideline","description":"Evidence-based international guideline resources for PCOS care.","icon":"🩺","url":"https://www.monash.edu/medicine/mchri/pcos/guideline"},
      {"id":"activity","title":"Physical activity","description":"CDC guidance for regular movement and health.","icon":"🚶‍♀️","url":"https://www.cdc.gov/physical-activity/"},
      {"id":"nutrition","title":"Healthy eating","description":"NIDDK general nutrition and weight-management guidance.","icon":"🥗","url":"https://www.niddk.nih.gov/health-information/weight-management/healthy-eating-nutrition"},
      {"id":"care","title":"Prepare for a visit","description":"Office on Women's Health information for healthcare visits.","icon":"📋","url":"https://www.womenshealth.gov/a-z-topics/health-care"}]}

@app.get("/api/backup")
def backup(db: Session=Depends(get_db), user: User=Depends(current_user)):
    return {"exported_at":datetime.utcnow().isoformat(),"profile":{"email":user.email,"name":user.name,"age":user.age,"height":user.height,"weight":user.weight},
        "screenings":screening_history(db,user),"cycles":get_cycles(db,user),"symptoms":get_symptoms(db,user)}

@app.post("/api/delete-account")
def delete_account(db: Session=Depends(get_db), user: User=Depends(current_user)):
    uid=user.id
    for model in [ScreeningResult,CycleEntry,SymptomEntry,Checkin,Conversation]:
        db.query(model).filter_by(user_id=uid).delete()
    db.delete(user); db.commit(); return {"message":"Account deleted"}
