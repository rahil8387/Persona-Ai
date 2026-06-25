import streamlit as st
import ollama
import pyttsx3
from datetime import datetime

# --- SETUP & PLATFORM STYLING ---
st.set_page_config(page_title="Persona AI", page_icon="🧬", layout="wide")

st.markdown("""
    <style>
        .main { background-color: #0A0D14; color: #E2E8F0; font-family: 'Inter', sans-serif; }
        .visual-panel {
            background: linear-gradient(145deg, #111625, #1A2035);
            border-radius: 16px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            border: 1px solid rgba(0, 255, 136, 0.1);
            margin-bottom: 20px;
            min-height: 460px;
        }
        h1 { color: #00FF88; text-align: center; font-weight: 800; letter-spacing: 3px; font-size: 2.5rem; }
        h3 { color: #00E5FF; font-weight: 600; letter-spacing: 1px; font-size: 1.1rem; margin-bottom: 15px; }
        .status-box { padding: 12px; border-radius: 8px; background: #070A10; border-left: 4px solid #00FF88; font-weight: bold; }
        
        .system-monitor {
            height: 320px; border-radius: 12px; background: #070A10;
            border: 1px solid #00E5FF; display: flex; flex-direction: column; 
            justify-content: center; align-items: center;
            box-shadow: 0 0 15px rgba(0, 229, 255, 0.2);
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1>PERSONA AI : INTERACTIVE DASHBOARD</h1>", unsafe_allow_html=True)
st.markdown("---")

# --- BACKEND SPEECH ENGINE ---
def speak_text_visual(text):
    """Speaks out loud cleanly"""
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 145)
        engine.say(text)
        engine.runAndWait()
        engine.stop()
        del engine
    except Exception as e:
        pass

def get_time_greeting():
    """Checks the computer clock and returns morning, afternoon, or evening greeting"""
    current_hour = datetime.now().hour
    if current_hour < 12:
        return "Good morning"
    elif 12 <= current_hour < 17:
        return "Good afternoon"
    else:
        return "Good evening"

def get_system_prompt(persona_name):
    if persona_name == "English Tutor":
        return "You are an encouraging English tutor virtual character. Converse in simple, short sentences."
    elif persona_name == "Admission Counselor":
        return "You are a professional University Admission Counselor. Speak entirely in Hindi/Hinglish."
    elif persona_name == "Medical Assistant":
        return "You are a compassionate medical assistant guide. Speak in Hindi/Hinglish."
    return "You are a helpful virtual character."

# --- SIDEBAR INTERFACE ---
st.sidebar.markdown("### 🧬 Select Persona")
persona_choice = st.sidebar.radio(
    "Choose Active Character:",
    ["English Tutor", "Admission Counselor", "Medical Assistant"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📡 Engine Status")
st.sidebar.markdown('<div class="status-box"><span style="color:#00FF88;">●</span> INTERACTION CORE LIVE</div>', unsafe_allow_html=True)

# --- CHAT MEMORY SYSTEMS ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Reset chat logs and trigger TIME-BASED spoken greeting if persona switches
if "active_persona" not in st.session_state or st.session_state.active_persona != persona_choice:
    st.session_state.active_persona = persona_choice
    st.session_state.messages = []
    
    # 1. Calculate time greeting automatically
    time_greeting = get_time_greeting()
    
    # 2. Build the personalized welcome phrase
    welcome_text = f"{time_greeting}! I am your Persona AI English Tutor. Let's practice speaking."
    if persona_choice == "Admission Counselor":
        welcome_text = f"{time_greeting}! Main Persona AI Counselor hoon. Main aapki admission mein kaise madad kar sakta hoon?"
    elif persona_choice == "Medical Assistant":
        welcome_text = f"{time_greeting}! Main aapka medical guide assistant hoon. Aap aaj kaisa mehsoos kar rahe hain?"
        
    st.session_state.messages.append({"role": "assistant", "content": welcome_text})
    
    # 3. Speak ONLY this initial greeting out loud
    speak_text_visual(welcome_text)

# --- MAIN STAGE LAYOUT ---
left_view, right_view = st.columns([5, 4])

with left_view:
    # SYSTEM INTERFACE VIEWPORT
    st.markdown('<div class="visual-panel">', unsafe_allow_html=True)
    st.markdown(f"<h3>⚡ SYSTEM MATRIX CORE: {persona_choice.upper()}</h3>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="system-monitor">
        <div style="font-size: 60px; margin-bottom: 15px;">🧠</div>
        <div style="font-weight: bold; letter-spacing: 2px; color: #00FF88; font-size: 18px;">PERSONA CORE ACTIVE</div>
        <div style="color: #00E5FF; font-size: 13px; font-family: monospace; margin-top: 5px;">SPOKEN GREETINGS TIME-ACTIVATED</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with right_view:
    # LIVE CONVERSATION TRANSCRIPT
    st.markdown('<div class="visual-panel">', unsafe_allow_html=True)
    st.markdown("<h3>📝 SYSTEM TRANSCRIPT</h3>", unsafe_allow_html=True)
    
    # Render messages cleanly (No automatic speaking during chat anymore)
    for msg in st.session_state.messages:
        speaker_label = "YOU" if msg["role"] == "user" else "AI"
        color = "#00E5FF" if speaker_label == "AI" else "#00FF88"
        
        st.markdown(f'<p style="color:{color}; margin-bottom: 2px;"><b>{speaker_label}:</b> {msg["content"]}</p>', unsafe_allow_html=True)
        st.markdown("<hr style='margin: 8px 0; border-color: rgba(255,255,255,0.05);'>", unsafe_allow_html=True)
        
    st.markdown('</div>', unsafe_allow_html=True)

# --- BOTTOM INPUT CHAT BAR ---
if user_input := st.chat_input("Communicate with Persona AI..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    system_instruction = get_system_prompt(persona_choice)
    
    response = ollama.chat(model='llama3.2:1b', messages=[
        {'role': 'system', 'content': system_instruction},
        {'role': 'user', 'content': user_input}
    ])
    
    ai_reply = response['message']['content']
    st.session_state.messages.append({"role": "assistant", "content": ai_reply})
    
    # Just refresh the screen text. Will remain completely silent!
    st.rerun()