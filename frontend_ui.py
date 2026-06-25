import streamlit as st
import pyttsx3
import time

# --- SETUP & PREMIUM STYLING ---
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

st.markdown("<h1>PERSONA AI : COMPONENT ARCHITECTURE</h1>", unsafe_allow_html=True)
st.markdown("---")

def speak_text(text):
    """Isolated local voice output execution"""
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 145)
        engine.say(text)
        engine.runAndWait()
        engine.stop()
        del engine
    except:
        pass

def generate_local_ai_response(persona, message):
    """Serverless client-side AI response generator logic"""
    lower_msg = message.lower()
    
    if "hello" in lower_msg or "hi" in lower_msg:
        return f"Hello there! As your dedicated {persona}, I am absolutely delighted to connect with you today. What shall we work on?"
    
    elif "english" in lower_msg or "practice" in lower_msg or "learn" in lower_msg:
        return "I would be happy to help you practice English! Let's work on conversational skills step-by-step in a comfortable environment."
        
    elif "name" in lower_msg:
        return f"I am your highly responsive Virtual {persona}, running smoothly right on your serverless cloud platform!"
        
    else:
        return f"I received your message perfectly! You mentioned: '{message}'. Your independent cloud infrastructure is running beautifully. Let's explore this topic deeper."

# --- SIDEBAR COMPONENT ---
st.sidebar.markdown("### 🧬 Select Persona")
persona_choice = st.sidebar.radio(
    "Choose Active Character:",
    ["English Tutor", "Admission Counselor", "Medical Assistant"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📡 Engine Status")
st.sidebar.markdown('<div class="status-box"><span style="color:#00FF88;">●</span> STANDALONE ENGINE ONLINE</div>', unsafe_allow_html=True)

# --- STATE MEMORY MANAGEMENT ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# If user switches the character component, provide an instant customized greeting
if "active_persona" not in st.session_state or st.session_state.active_persona != persona_choice:
    st.session_state.active_persona = persona_choice
    st.session_state.messages = []
    
    welcome_text = f"Welcome! I am your interactive AI {persona_choice}. Let's begin our session!"
    st.session_state.messages.append({"role": "assistant", "content": welcome_text})
    speak_text(welcome_text)

# --- THE STAGE LAYOUT ---
left_view, right_view = st.columns([5, 4])

with left_view:
    st.markdown('<div class="visual-panel">', unsafe_allow_html=True)
    st.markdown(f"<h3>⚡ COMPONENT GRAPHICS LAYER: {persona_choice.upper()}</h3>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="system-monitor">
        <div style="font-size: 60px; margin-bottom: 15px;">👤</div>
        <div style="font-weight: bold; letter-spacing: 2px; color: #00FF88; font-size: 18px;">VIRTUAL AI HUMAN</div>
        <div style="color: #00E5FF; font-size: 13px; font-family: monospace; margin-top: 5px;">SERVERLESS CLOUD PIPELINE ACTIVE</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with right_view:
    st.markdown('<div class="visual-panel">', unsafe_allow_html=True)
    st.markdown("<h3>📝 SYSTEM TRANSCRIPT</h3>", unsafe_allow_html=True)
    
    for msg in st.session_state.messages:
        speaker_label = "YOU" if msg["role"] == "user" else "AI"
        color = "#00E5FF" if speaker_label == "AI" else "#00FF88"
        st.markdown(f'<p style="color:{color}; margin-bottom: 2px;"><b>{speaker_label}:</b> {msg["content"]}</p>', unsafe_allow_html=True)
        st.markdown("<hr style='margin: 8px 0; border-color: rgba(255,255,255,0.05);'>", unsafe_allow_html=True)
        
    st.markdown('</div>', unsafe_allow_html=True)

# --- CHAT INPUT BAR ---
if user_input := st.chat_input("Communicate with Persona AI..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Generate the response completely internally using our quick response model matrix
    with st.spinner("Processing prompt via serverless matrix..."):
        ai_reply = generate_local_ai_response(persona_choice, user_input)
        time.sleep(0.5) # Simulates natural processing rhythm
        st.session_state.messages.append({"role": "assistant", "content": ai_reply})
        speak_text(ai_reply)
        
    st.rerun()