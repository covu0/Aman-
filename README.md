# 🛡️ أمان | Aman

نظام كشف الاحتيال المالي - تحقّق قبل التحويل

## 📁 هيكل المشروع

```
aman-organized/
├── main.py              # الخادم الرئيسي (FastAPI)
├── requirements.txt     # المكتبات المطلوبة
├── .env                 # المفاتيح السرية (لا تشاركه!)
├── .env.example         # مثال للمفاتيح
├── .gitignore           # الملفات المتجاهلة
├── static/
│   ├── style.css        # التنسيقات
│   └── script.js        # الجافاسكربت
└── templates/
    └── index.html       # الصفحة الرئيسية
```

## 🚀 طريقة التشغيل

1. تثبيت المكتبات:
```bash
pip install -r requirements.txt
```

2. إعداد المفاتيح:
```bash
# انسخ ملف المثال
cp .env.example .env

# عدّل الملف وضع مفاتيحك
```

3. تشغيل الخادم:
```bash
python main.py
```

4. افتح المتصفح:
```
http://localhost:8000
```

## 🔐 الأمان

- المفاتيح محفوظة في ملف `.env` منفصل
- ملف `.gitignore` يمنع رفع المفاتيح للـ Git
- لا تشارك ملف `.env` مع أحد!

## 🛠️ التقنيات المستخدمة

- **Backend:** Python + FastAPI
- **Frontend:** HTML + CSS + JavaScript
- **NLP:** معالجة لغة طبيعية
- **Rule Engine:** محرك قواعد للكشف

## 👥 الفريق

جادة ثون 2025
