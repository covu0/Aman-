// Examples data
const examples = {
    1: "تم إيقاف بطاقتك البنكية، حدث بياناتك فوراً عبر الرابط: bank-update.xyz",
    2: "مبروك! ربحت 50,000 ريال من البنك الأهلي. أرسل رقم بطاقتك على 0599999999",
    3: "أنا خويك من المدرسة، محتاج 1000 ريال ضروري وأرجعها لك بكرة والله",
    4: "الراجحي: تم تحويل 500 ريال لحسابك من عبدالله. الرصيد: 3,250 ريال"
};

// Set example text
function setExample(n) { 
    document.getElementById('msg').value = examples[n]; 
}

// Show/Hide popups
function showWhy() { 
    document.getElementById('whyPopup').style.display = 'flex'; 
}

function showActions() { 
    document.getElementById('actionsPopup').style.display = 'flex'; 
}

function closePopup(id) { 
    document.getElementById(id).style.display = 'none'; 
}

// Main analyze function
async function analyze() {
    const msg = document.getElementById('msg').value.trim();
    if (!msg) { 
        alert('الصق الرسالة أولاً'); 
        return; 
    }
    
    document.getElementById('loading').style.display = 'block';
    document.getElementById('result').style.display = 'none';
    
    try {
        const res = await fetch('/analyze', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({text: msg})
        });
        const data = await res.json();
        showResult(data);
    } catch(e) { 
        alert('حدث خطأ، حاول مرة أخرى'); 
    }
    
    document.getElementById('loading').style.display = 'none';
}

// Display result
function showResult(data) {
    const score = data.risk_score || 0;
    const card = document.getElementById('resultCard');
    const level = score >= 70 ? 'danger' : score >= 40 ? 'warning' : 'safe';
    
    card.className = 'result-card ' + level;
    
    document.getElementById('alertIcon').textContent = score >= 70 ? '🚨' : score >= 40 ? '⚠️' : '✅';
    document.getElementById('alertTitle').textContent = score >= 70 ? 'تحذير أمني - خطر عالي' : score >= 40 ? 'رسالة مشبوهة' : 'رسالة آمنة';
    document.getElementById('scoreValue').textContent = score + '%';
    document.getElementById('threatType').textContent = data.threat_type || 'غير محدد';
    document.getElementById('analysisText').textContent = data.reason || 'لم يتم الكشف عن تهديد';
    document.getElementById('adviceText').textContent = data.advice || 'تأكد دائماً من المصدر';
    
    // Update safety bar
    const bars = [document.getElementById('bar1'), document.getElementById('bar2'), document.getElementById('bar3')];
    bars.forEach((bar, i) => {
        bar.className = 'bar-section';
        if (level === 'safe' && i === 0) bar.classList.add('active', 'safe');
        if (level === 'warning' && i <= 1) bar.classList.add('active', 'warning');
        if (level === 'danger') bar.classList.add('active', 'danger');
    });
    
    // Update action buttons
    const actionsDiv = document.getElementById('actionBtns');
    if (score < 40) {
        actionsDiv.innerHTML = '<button class="action-btn btn-verify" style="background:#00ba7c;border:none;color:#fff;">✅ الرسالة آمنة</button>';
    } else {
        actionsDiv.innerHTML = '<button class="action-btn btn-ignore">🚫 تجاهل الرسالة</button><button class="action-btn btn-verify" onclick="showActions()">ماذا أفعل الآن؟</button>';
    }
    
    document.getElementById('result').style.display = 'block';
    document.getElementById('result').scrollIntoView({ behavior: 'smooth' });
}
