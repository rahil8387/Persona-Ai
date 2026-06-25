import streamlit as st
import ollama
import pyttsx3
import os

# --- SETUP & HIGH-TECH STYLING ---
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
            min-height: 480px;
        }
        h1 { color: #00FF88; text-align: center; font-weight: 800; letter-spacing: 3px; font-size: 2.5rem; }
        h3 { color: #00E5FF; font-weight: 600; letter-spacing: 1px; font-size: 1.1rem; margin-bottom: 15px; }
        .status-box { padding: 12px; border-radius: 8px; background: #070A10; border-left: 4px solid #00FF88; font-weight: bold; }
        video { border-radius: 12px; border: 1px solid rgba(0, 229, 255, 0.2); }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1>PERSONA AI : VIRTUAL HUMAN INTERFACE</h1>", unsafe_allow_html=True)
st.markdown("---")

# --- BACKEND SPEECH ENGINE ---
def speak_text_visual(text):
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 145)
        engine.say(text)
        engine.runAndWait()
        engine.stop()
        del engine
    except Exception as e:
        pass

def get_system_prompt(persona_name):
    if persona_name == "English Tutor":
        return "You are an encouraging English tutor virtual human. Converse in simple, short sentences."
    elif persona_name == "Admission Counselor":
        return "You are a professional University Admission Counselor virtual human. Speak entirely in Hindi/Hinglish."
    elif persona_name == "Medical Assistant":
        return "You are a compassionate medical assistant virtual human guide. Speak in Hindi/Hinglish."
    return "You are a helpful virtual character."

# --- SIDEBAR INTERFACE ---
st.sidebar.markdown("### 🧬 Select Persona")
persona_choice = st.sidebar.radio(
    "Choose Active Character:",
    ["English Tutor", "Admission Counselor", "Medical Assistant"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📡 Engine Status")
st.sidebar.markdown('<div class="status-box"><span style="color:#00FF88;">●</span> HUMAN CORE ACTIVE</div>', unsafe_allow_html=True)

# --- CHAT & REFRESH MEMORY ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if "active_persona" not in st.session_state or st.session_state.active_persona != persona_choice:
    st.session_state.active_persona = persona_choice
    st.session_state.messages = []
    
    welcome_text = "Hello! My visual system is online. I am your Persona AI English Tutor."
    if persona_choice == "Admission Counselor":
        welcome_text = "Namaste! Main Persona AI Counselor hoon. Admission ke baare mein puchiye."
    elif persona_choice == "Medical Assistant":
        welcome_text = "Namaste! Main aapka healthcare assistant hoon. Aap aaj kaisa mehsoos kar rahe hain?"
        
    st.session_state.messages.append({"role": "assistant", "content": welcome_text})
    speak_text_visual(welcome_text)

# --- MAIN STAGE LAYOUT ---
left_view, right_view = st.columns([5, 4])

with left_view:
    # VIRTUAL HUMAN VIDEO VIEWPORT
    st.markdown('<div class="visual-panel">', unsafe_allow_html=True)
    st.markdown(f"<h3>👤 LIVE STREAM: {persona_choice.upper()} AVATAR</h3>", unsafe_allow_html=True)
    
    # Check if local video file exists, otherwise show high-tech digital shadow human placeholder
    if os.path.exists("avatar.mp4"):
        video_file = open("avatar.mp4", "rb")
        video_bytes = video_file.read()
        st.video(video_bytes, start_time=0, autoplay=True, loop=True, muted=True)
    else:
        # High-tech animated human silhouette CSS placeholder
        html_placeholder = """
        <div style="background: radial-gradient(circle, #1F263B 0%, #070A10 100%); 
                    height: 360px; border-radius: 12px; display: flex; 
                    justify-content: center; align-items: center; border: 1px dashed #00E5FF;">
            <div style="text-align: center; color: #00E5FF;">
                <div style="font-size: 80px; margin-bottom: 10px;">👤</div>
                <div style="font-weight: bold; letter-spacing: 1px;">VIRTUAL HUMAN STREAM READY</div>
                <div style="color: #666; font-size: 12px; margin-top: 5px;">Place 'avatar.mp4' in project folder to render your 3D character clip</div>
            </div>
        </div>
        """
        st.components.v1.html(html_placeholder, height=370)
        
    st.markdown('</div>', unsafe_allow_html=True)

with right_view:
    # DIGITAL TRANSCRIPT VIEWPORT
    st.markdown('<div class="visual-panel">', unsafe_allow_html=True)
    st.markdown("<h3>📝 LIVE TRANSCRIPT</h3>", unsafe_allow_html=True)
    
    for msg in st.session_state.messages:
        speaker_label = "YOU" if msg["role"] == "user" else "AI"
        color = "#00E5FF" if speaker_label == "AI" else "#00FF88"
        st.markdown(f'<p style="color:{color}; margin-bottom: 8px;"><b>{speaker_label}:</b> {msg["content"]}</p>', unsafe_allow_html=True)
        
    st.markdown('</div>', unsafe_allow_html=True)

# --- BOTTOM USER INPUT PANEL ---
if user_input := st.chat_input("Talk to the virtual human..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    system_instruction = get_system_prompt(persona_choice)
    
    response = ollama.chat(model='llama3.2:1b', messages=[
        {'role': 'system', 'content': system_instruction},
        {'role': 'user', 'content': user_input}
    ])
    
    ai_reply = response['message']['content']
    st.session_state.messages.append({"role": "assistant", "content": ai_reply})
    
    st.rerun()

# Run voice loop out loud
if len(st.session_state.messages) > 1 and st.session_state.messages[-1]["role"] == "assistant":
    speak_text_visual(st.session_state.messages[-1]["content"])