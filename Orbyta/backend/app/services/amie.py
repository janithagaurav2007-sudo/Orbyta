"""Local, safety-first women’s reproductive-health assistant.

This is intentionally deterministic so the demo works without an external AI key.
It uses intent matching plus the user's Orbyta context. It is educational, not diagnostic.
"""
import re

DISCLAIMER = "I’m an educational health companion, not a clinician. I can explain health topics and your Orbyta data, but I can’t diagnose, prescribe, or replace urgent medical care."

TOPICS = {
    "pcos": "PCOS is a common hormonal condition that can affect ovulation and periods and may be associated with higher androgen activity and metabolic features. Symptoms vary widely, and having one symptom does not mean someone has PCOS.",
    "pcos_symptoms": "PCOS can be associated with irregular or infrequent periods, acne, increased facial/body hair, scalp hair thinning and some metabolic features. These symptoms also have other possible causes, so they need context.",
    "periods": "Period timing varies between people. Repeatedly very irregular, unusually long, or absent periods are worth tracking and discussing with a healthcare professional, especially if this is a change from your usual pattern.",
    "fertility": "PCOS can make ovulation less predictable for some people, which can affect conception, but PCOS does not automatically mean infertility. Many people with PCOS can become pregnant with appropriate care.",
    "contraception": "Contraception choices depend on pregnancy goals, bleeding patterns, medical history, medications and personal preferences. Options include condoms, pills, patches, rings, injections, implants and intrauterine devices. A clinician or pharmacist can help compare suitability and side effects.",
    "pregnancy": "If you might be pregnant and have a missed period, a home pregnancy test is a practical first step. Severe pain, fainting, shoulder-tip pain or heavy bleeding during a possible pregnancy needs urgent medical assessment.",
    "sexual_health": "Sexual and reproductive health includes contraception, STI prevention/testing, consent, pain, libido and pregnancy planning. Condoms can reduce STI and pregnancy risk, while other contraceptives mainly prevent pregnancy rather than STIs.",
    "menopause": "Menopause is reached after 12 months without a menstrual period when there is no other explanation. Perimenopause can involve changing cycle timing, hot flashes, sleep changes and mood symptoms. New or heavy bleeding after menopause should be assessed by a clinician.",
    "nutrition": "For general metabolic health, aim for balanced, sustainable eating rather than crash diets. Meals can include vegetables or fruit, fibre-rich carbohydrates, protein and healthy fats. Individual nutrition needs differ, especially during pregnancy or with medical conditions.",
    "exercise": "Regular movement can support cardiovascular and metabolic health. A realistic mix of walking or other aerobic activity, strength work and everyday movement is usually more sustainable than an extreme routine.",
    "sleep_stress": "Sleep and stress are important wellbeing signals but are not diagnostic tests for PCOS. Consistent sleep routines, daylight exposure, movement and manageable stress-reduction practices can be useful.",
}

def _risk_answer(context):
    s=context.get("screening")
    if not s:
        return "You haven’t completed a screening yet. Open PCOS Screening to create an estimate, then I can explain what the result and contributing patterns mean."
    factors=s.get("factors") or []
    factor_text=(" The main associated patterns flagged were: " + ", ".join(factors) + ".") if factors else " No specific associated features were flagged in the saved result."
    return f"Your latest Orbyta screening estimate is {s.get('percentage')}% ({s.get('level')}). This is a screening estimate, not a diagnosis.{factor_text} A clinician uses history, examination and sometimes tests to assess PCOS."

def _personal_context(context):
    user=context.get("user",{})
    parts=[]
    if user.get("bmi") is not None: parts.append(f"your recorded BMI is {user['bmi']}")
    if context.get("symptom_count"): parts.append(f"you have logged {context['symptom_count']} symptom entries")
    if context.get("cycle_count"): parts.append(f"you have logged {context['cycle_count']} cycle patterns")
    return ", ".join(parts)

def _urgent(message):
    t=message.lower()
    urgent_patterns=[
        r"heavy bleeding",r"soaking.*pad",r"faint",r"passed out",r"severe pain",r"worst pain",
        r"chest pain",r"trouble breathing",r"difficulty breathing",r"suicid",r"self[- ]?harm",
        r"pregnan.*(pain|bleed)",r"ectopic",r"severe headache.*vision"
    ]
    return any(re.search(p,t) for p in urgent_patterns)

def reply(message,context):
    t=message.lower().strip()
    if _urgent(t):
        return "Some symptoms can need urgent medical attention. If you have severe pain, fainting, difficulty breathing, very heavy bleeding, or pregnancy with significant pain/bleeding, please seek urgent medical care or your local emergency service now. I can’t safely assess an emergency in chat."
    if any(x in t for x in ["my risk","my score","my percentage","screening result","screening likelihood","risk score"]):
        return _risk_answer(context)
    if any(x in t for x in ["what is pcos","pcos mean","tell me about pcos","pcos?"]):
        return TOPICS["pcos"]
    if any(x in t for x in ["pcos symptom","symptoms of pcos","signs of pcos"]):
        return TOPICS["pcos_symptoms"]
    if any(x in t for x in ["period","cycle","missed period","late period","irregular period"]):
        return TOPICS["periods"]
    if any(x in t for x in ["fertility","fertile","ovulation","conceive","trying to get pregnant"]):
        return TOPICS["fertility"]
    if any(x in t for x in ["contraception","birth control","pregnancy prevention","condom","pill","iud","implant"]):
        return TOPICS["contraception"]
    if any(x in t for x in ["pregnant","pregnancy test","pregnancy"]):
        return TOPICS["pregnancy"]
    if any(x in t for x in ["sti","std","sexual health","sexually transmitted"]):
        return TOPICS["sexual_health"]
    if any(x in t for x in ["menopause","perimenopause","hot flash"]):
        return TOPICS["menopause"]
    if any(x in t for x in ["diet","food","nutrition","eat","meal","weight loss"]):
        return TOPICS["nutrition"]
    if any(x in t for x in ["exercise","workout","activity","walking","gym"]):
        return TOPICS["exercise"]
    if any(x in t for x in ["sleep","stress","anxiety","wellness"]):
        return TOPICS["sleep_stress"]
    if any(x in t for x in ["cause","causes","why do i have pcos"]):
        return "There is no single cause of PCOS. It is associated with genetic susceptibility, hormonal signalling and metabolic factors such as insulin resistance. It is not simply caused by lifestyle, and a person's symptoms are not a measure of personal failure."
    if any(x in t for x in ["prevent","prevention","avoid pcos","reduce risk"]):
        return "There is no guaranteed way to prevent PCOS itself. Preventive health is about noticing persistent changes early and supporting overall health: sustainable movement, balanced nutrition, adequate sleep, stress management and appropriate weight management when relevant. Avoid crash diets or extreme routines."
    if any(x in t for x in ["doctor","doctor visit","when should i","when to see","clinician","hospital"]):
        return "Consider a clinician conversation if your periods become persistently irregular or absent, symptoms are worsening, you are concerned about fertility, or a symptom is persistent or disruptive. Take your Orbyta report and cycle/symptom history with you."
    if any(x in t for x in ["my data","my profile","what have i logged","what do you know"]):
        personal=_personal_context(context)
        return f"From your Orbyta profile, I can see {personal or 'only the information you have entered so far'}. I use that context to explain your Orbyta results, but I don’t treat it as a diagnosis."
    return "I can help with PCOS, periods and cycle patterns, symptoms, fertility basics, contraception, pregnancy questions, sexual/reproductive health, menopause, nutrition, exercise, sleep/stress, your Orbyta screening result, and when to seek care. What would you like to know?"
