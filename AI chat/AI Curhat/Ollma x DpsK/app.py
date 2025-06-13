from flask import Flask, request, jsonify, render_template, Response
import ollama
import time
from textblob import TextBlob
from datetime import datetime

app = Flask(__name__)

# Store chat history
chat_sessions = {}

# Enhanced user data with marital status
USER_DATA = {
    "name": "David",
    "age": 40,
    "status": "Senior Manager",
    "job": "Project Manager",
    "marital_status": "Married"
}


PROMPT_SYSTEM = (
    "Kamu adalah teman curhat virtual yang responsif dan empatik. Sesuaikan gaya bahasa dan respons berdasarkan usia dan status pengguna."
    "\n\nPanduan Respons Berdasarkan Usia:"
    "\n1. Usia ≤ 25 tahun (Young Adult):"
    "\n   - Gunakan bahasa santai dan akrab dengan konsisten menggunakan 'aku-kamu'"
    "\n   - Contoh sapaan: 'Hai!', 'Halo!'"
    "\n   - Fokus pada topik: kuliah, karir awal, relationship, self-discovery"
    "\n2. Usia > 25 tahun (Professional Adult):"
    "\n   - Gunakan bahasa yang lebih matang tapi tetap ramah dengan konsisten menggunakan 'saya-Anda'"
    "\n   - Contoh sapaan: 'Selamat [waktu]', 'Halo'"
    "\n   - Fokus pada topik: karir, keluarga, investasi, pengembangan diri"
    "\n\nPanduan Respons Berdasarkan Status Pernikahan:"
    "\n1. Single:"
    "\n   - Topik: pengembangan diri, karir, relationship"
    "\n   - Contoh: 'Bagaimana dengan rencana pengembangan diri?'"
    "\n2. Married:"
    "\n   - Topik: keseimbangan kerja-keluarga, relationship, perencanaan masa depan"
    "\n   - Contoh: 'Bagaimana dengan keseimbangan waktu kerja dan keluarga?'"
    "\n\nFormat Respons:"
    "\n1. Untuk keluhan/masalah:"
    "- Usia ≤ 25: 'Aku mengerti perasaanmu. Yuk kita cari solusinya bareng-bareng!'"
    "- Usia > 25: 'Saya memahami situasi Anda. Mari kita diskusikan solusinya bersama.'"
    "\n2. Untuk kabar baik:"
    "- Usia ≤ 25: 'Wah, aku senang mendengarnya! Cerita lebih detail dong!'"
    "- Usia > 25: 'Senang sekali mendengar kabar baik ini. Bisa diceritakan lebih detail?'"
    "\n3. Untuk situasi netral:"
    "- Usia ≤ 25: 'Menurutmu, apa yang bisa membuat situasinya jadi lebih baik?'"
    "- Usia > 25: 'Menurut Anda, apa yang bisa meningkatkan situasi ini?'"
)

def analyze_sentiment(text):
    blob = TextBlob(text)
    return blob.sentiment.polarity

def get_age_appropriate_language(age, marital_status):
    if age <= 25:
        style = {
            "tone": "santai dan akrab",
            "pronouns": "aku-kamu",
            "greetings": ["Hai!", "Halo!"],
            "focus": "masalah kuliah, karir awal, relationship" if marital_status == "Single" 
                    else "keseimbangan kuliah/karir dengan keluarga"
        }
    else:
        style = {
            "tone": "matang dan ramah",
            "pronouns": "saya-Anda",
            "greetings": ["Selamat pagi/siang/sore", "Halo"],
            "focus": "pengembangan karir, investasi" if marital_status == "Single"
                    else "keseimbangan karir-keluarga"
        }
    return style

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "").strip()
    session_id = data.get("session_id", "default")
    
    if not user_message:
        return jsonify({"error": "Pesan tidak boleh kosong"}), 400
    
    if session_id not in chat_sessions:
        chat_sessions[session_id] = []
    
    # Analyze sentiment
    sentiment_score = analyze_sentiment(user_message)
    
    # Get age-appropriate language style
    language_style = get_age_appropriate_language(USER_DATA['age'], USER_DATA['marital_status'])
    
    # Build prompt with user context
    custom_prompt = PROMPT_SYSTEM
    user_context = (
        f"\n\nKonteks Pengguna:"
        f"\n- Nama: {USER_DATA['name']}"
        f"\n- Usia: {USER_DATA['age']}"
        f"\n- Status: {USER_DATA['status']}"
        f"\n- Pekerjaan: {USER_DATA['job']}"
        f"\n- Status Pernikahan: {USER_DATA['marital_status']}"
        f"\n\nGaya Bahasa:"
        f"\n- Tone: {language_style['tone']}"
        f"\n- Penggunaan Kata Ganti: {language_style['pronouns']}"
        f"\n- Fokus Topik: {language_style['focus']}"
    )
    
    custom_prompt += user_context
    
    sentiment_prompt = (
        "Respons dengan semangat dan optimisme yang sesuai dengan usia pengguna."
        if sentiment_score > 0.25
        else "Tunjukkan empati dan dukungan yang sesuai dengan usia dan status pengguna."
        if sentiment_score < -0.25
        else "Ajukan pertanyaan yang relevan dengan usia dan situasi pengguna."
    )
    
    chat_sessions[session_id].append({
        "role": "user",
        "content": user_message,
        "timestamp": datetime.now().isoformat()
    })
    
    messages = [{"role": "system", "content": f"{custom_prompt} {sentiment_prompt}"}]
    messages.extend(
        {"role": msg["role"], "content": msg["content"]}
        for msg in chat_sessions[session_id][-10:]
    )
    
    def generate():
        response = ollama.chat(model="llama3.1", messages=messages)
        ai_response = response["message"]["content"]
        
        chat_sessions[session_id].append({
            "role": "assistant",
            "content": ai_response,
            "timestamp": datetime.now().isoformat()
        })
        
        words = ai_response.split()
        output = ""
        for word in words:
            output += word + " "
            yield output
            time.sleep(0.05)
    
    return Response(generate(), content_type="text/plain")

@app.route("/history/<session_id>", methods=["GET"])
def get_history(session_id):
    if session_id not in chat_sessions:
        return jsonify([])
    return jsonify(chat_sessions[session_id])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)