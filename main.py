from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
from pydantic import BaseModel
from dotenv import load_dotenv
import httpx
import json
import os

# تحميل المتغيرات من ملف .env
load_dotenv()

# قراءة المفاتيح من البيئة
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OCR_API_KEY = os.getenv("OCR_API_KEY")

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# ربط الملفات الثابتة والقوالب
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

class Message(BaseModel):
    text: str

def rule_based_score(text: str) -> int:
    """محرك القواعد - يحسب نسبة الخطر بناءً على الكلمات المفتاحية"""
    score = 0
    keywords = {
        "تحويل": 20, "حول": 20, "حولي": 25, "ارسل": 15, "ارسلي": 15,
        "رابط": 25, "http": 25, "bit.ly": 30, ".xyz": 30, ".top": 30,
        "فوراً": 15, "فورا": 15, "الآن": 15, "الان": 15, "عاجل": 15,
        "إيقاف": 20, "ايقاف": 20, "تجميد": 20, "تحديث": 15,
        "بطاقتك": 20, "حسابك": 20, "بياناتك": 20,
        "جائزة": 25, "ربحت": 25, "مبروك": 20, "فزت": 25,
        "محتاج": 20, "ضروري": 15, "سلفني": 25, "قرض": 20
    }
    for word, value in keywords.items():
        if word in text:
            score += value
    return min(score, 100)

def detect_threat_type(text: str) -> str:
    """تصنيف نوع التهديد"""
    if any(w in text for w in ["خويك", "صاحبك", "قريبك", "أخوك", "محتاج", "سلفني"]):
        return "احتيال اجتماعي - استغلال الثقة"
    elif any(w in text for w in ["إيقاف", "ايقاف", "تجميد", "حسابك", "بطاقتك"]):
        return "انتحال صفة بنك"
    elif any(w in text for w in ["ربحت", "جائزة", "مبروك", "فزت"]):
        return "جوائز وهمية"
    elif any(w in text for w in [".xyz", ".top", "bit.ly", "http"]):
        return "روابط تصيد احتيالي"
    elif any(w in text for w in ["حول", "حولي", "ارسل", "تحويل"]):
        return "طلب تحويل مالي مشبوه"
    return "رسالة عادية"

def get_reason_from_text(text: str) -> str:
    """استخراج سبب التحذير من محتوى الرسالة"""
    reasons = []
    
    if any(w in text for w in ["خويك", "صاحبك", "قريبك", "أخوك"]):
        reasons.append("شخص يدّعي معرفتك")
    if any(w in text for w in ["محتاج", "سلفني", "ضروري"]):
        reasons.append("طلب مال عاجل")
    if any(w in text for w in ["إيقاف", "ايقاف", "تجميد"]):
        reasons.append("تهديد بإيقاف الحساب")
    if any(w in text for w in ["حسابك", "بطاقتك", "بياناتك"]):
        reasons.append("طلب معلومات حساسة")
    if any(w in text for w in ["ربحت", "جائزة", "مبروك", "فزت"]):
        reasons.append("ادعاء فوز بجائزة")
    if any(w in text for w in [".xyz", ".top", "bit.ly", "http"]):
        reasons.append("رابط مشبوه")
    if any(w in text for w in ["فوراً", "فورا", "الآن", "الان", "عاجل"]):
        reasons.append("استعجال وضغط")
    if any(w in text for w in ["حول", "حولي", "ارسل", "تحويل"]):
        reasons.append("طلب تحويل مال")
    if any(w in text for w in ["تحديث"]):
        reasons.append("طلب تحديث بيانات")
    
    if reasons:
        return "الرسالة تحتوي على: " + "، ".join(reasons)
    return "لم يتم الكشف عن مؤشرات احتيال واضحة"

def get_advice(score: int, text: str) -> str:
    """إعطاء نصيحة مناسبة"""
    if score < 40:
        return "الرسالة تبدو آمنة، لكن تأكد دائماً من هوية المرسل"
    
    if any(w in text for w in ["خويك", "صاحبك", "قريبك", "أخوك"]):
        return "تأكد من هوية الشخص بالاتصال المباشر قبل أي تحويل"
    elif any(w in text for w in ["إيقاف", "ايقاف", "تجميد", "بطاقتك"]):
        return "لا تضغط على أي رابط واتصل على رقم البنك الرسمي للتأكد"
    elif any(w in text for w in ["ربحت", "جائزة", "مبروك"]):
        return "لا يوجد جوائز حقيقية عبر الرسائل، تجاهل الرسالة"
    elif any(w in text for w in [".xyz", ".top", "bit.ly"]):
        return "لا تضغط على الرابط، قد يكون موقع تصيد احتيالي"
    else:
        return "كن حذراً ولا تشارك بياناتك أو تحوّل أي مبلغ"

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/analyze")
async def analyze(msg: Message):
    # حساب النتيجة من القواعد المحلية
    rule_score = rule_based_score(msg.text)
    threat_type = detect_threat_type(msg.text)
    local_reason = get_reason_from_text(msg.text)
    
    # تحليل بالنموذج اللغوي
    prompt = f"""أنت محلل أمني للرسائل النصية في السعودية.

حلل هذه الرسالة:
"{msg.text}"

مهم جداً:
- لا تذكر "رابط" إلا إذا كان هناك رابط فعلي (http, .com, .xyz, bit.ly)
- لا تذكر "تحويل" إلا إذا طُلب تحويل مال فعلاً
- كن دقيقاً جداً في وصف ما تحتويه الرسالة

أرجع JSON فقط:
{{"label": "Safe/Suspicious/Scam", "risk_score": 0-100}}"""

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
                json={"model": "llama-3.1-8b-instant", "messages": [{"role": "user", "content": prompt}], "temperature": 0.2},
                timeout=30.0
            )
            data = response.json()
            
            if "error" not in data:
                text = data["choices"][0]["message"]["content"].strip()
                text = text.replace("```json", "").replace("```", "").strip()
                ai_result = json.loads(text)
                ai_score = ai_result.get("risk_score", 0)
                
                # دمج النتائج
                final_score = min(int((rule_score * 0.6) + (ai_score * 0.4)), 100)
            else:
                final_score = rule_score
    except:
        final_score = rule_score
    
    advice = get_advice(final_score, msg.text)
    
    return {
        "risk_score": final_score,
        "reason": local_reason,
        "advice": advice,
        "threat_type": threat_type
    }

if __name__ == "__main__":
    import uvicorn
    print("=" * 40)
    print("🛡️  أمان | Aman")
    print("=" * 40)
    print("http://localhost:8000")
    print("=" * 40)
    uvicorn.run(app, host="0.0.0.0", port=8000)
