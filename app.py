import streamlit as st
import ollama
import os
import time
import speech_recognition as sr
import database

# --- LAYER 3: DATABASE LOG SYNC ---
database.init_db()

# --- APPLICATION VIEW ARCHITECTURE ---
st.set_page_config(page_title="Virtual Consultant", page_icon="👔", layout="wide")

st.markdown("""
    <style>
        /* Base Google Meet Desktop Aesthetic */
        .stApp {
            background-color: #202124 !important;
            color: #E8EAED !important;
            font-family: 'Inter', system-ui, "Apple Color Emoji", "Segoe UI Emoji", sans-serif !important;
        }

        /* Video Container (Column 1) via Streamlit's native data-testid */
        [data-testid="column"]:nth-child(1) {
            background-color: #171717;
            border-radius: 12px;
            height: 580px;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
            padding: 0 !important;
        }
        
        [data-testid="stVideo"] {
            width: 400px !important;
            height: 580px !important;
        }

        [data-testid="stVideo"] video {
            object-fit: contain !important; 
            width: 100% !important;
            height: 100% !important;
        }

        /* Meet Chat Sidebar Panel (Column 2) */
        [data-testid="column"]:nth-child(2) {
            background-color: #2D2E31;
            height: 580px;
            border-radius: 12px;
            padding: 20px !important;
            overflow-y: auto;
            border: 1px solid rgba(255,255,255,0.08);
        }
        
        .meet-msg-bubble {
            font-size: 16px;
            margin-bottom: 12px;
            line-height: 1.5;
            white-space: pre-wrap;
        }
        .msg-user { color: #8AB4F8; }
        .msg-ai { color: #E8EAED; }

        /* Utility Control Belt */
        .utility-belt {
            margin-top: 24px;
            padding: 16px;
        }

        /* Hide Top UI and Padding */
        .block-container { padding-top: 2rem !important; }
        header { visibility: hidden; }
        footer { visibility: hidden; }
    </style>
""", unsafe_allow_html=True)

# --- BACKEND MODEL INFRASTRUCTURE PIPELINE ---

# Layer 1: Speech-to-Text
def listen_to_microphone():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        try:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            text_query = recognizer.recognize_google(audio)
            return text_query
        except Exception:
            return None

# --- CONTEXT STATE MANAGERS ---
if "state" not in st.session_state:
    st.session_state.state = 1 # 1: Portal, 2: Meet Room
if "messages" not in st.session_state:
    st.session_state.messages = []
if "meet_loader" not in st.session_state:
    st.session_state.meet_loader = False
if "camera_on" not in st.session_state:
    st.session_state.camera_on = True
if "presenting" not in st.session_state:
    st.session_state.presenting = False

# Profile Selection
st.sidebar.markdown("### 🧑‍💼 Select Profile")
profile_choice = st.sidebar.radio(
    "Available Consultants:",
    ["English Tutor", "Admission Counselor", "Medical Counselor"]
)

video_map = {
    "English Tutor": "Tutor.mp4",
    "Admission Counselor": "counselor.mp4",
    "Medical Counselor": "medical.mp4"
}
target_video = video_map[profile_choice]

if "last_profile" not in st.session_state or st.session_state.last_profile != profile_choice:
    st.session_state.last_profile = profile_choice
    st.session_state.messages = []
    st.session_state.state = 1

def get_system_instruction():
    if st.session_state.state == 1:
        return (
            "You are a warm, polite, and welcoming human receptionist. "
            "If the user says hello, greetings, or asks who you are/how you can help, reply politely in a relaxed way to make them feel comfortable. "
            "Let them know you can help connect them to an expert consultant. "
            "If the user asks to connect, meet, call, talk, or requests an expert, confirm warmly that you are transferring them right now. "
            "Always respond directly to the user's actual prompt. Do not repeat what the user said. "
            "By default, speak in natural, flowing conversational sentences without bullet points. However, if the user explicitly asks for a chart, list, or structured format, you must provide it."
        )
    else:
        return (
            f"You are a warm, polite, and highly knowledgeable {profile_choice} on a live video call. "
            "You speak naturally, like a real human in a relaxed, friendly setting. "
            "If the user greets you or asks who you are, introduce yourself warmly. "
            "Always pay close attention to the user's prompt and give an accurate, helpful response. "
            "Keep your answers concise and conversational, as they are being spoken out loud. Do not repeat what the user said. "
            "CRITICAL RULE: By default, speak ONLY in short, continuous, natural conversational paragraphs without bullet points. HOWEVER, if the user explicitly asks for a chart, table, list, or structured layout, you MUST provide it exactly as requested."
        )

# =========================================================================
# STATE 1: PRE-SCREENING PORTAL
# =========================================================================
if st.session_state.state == 1:
    st.title("🛡️ Automated Pre-Screening Portal")
    st.markdown("Welcome to the workspace. How can we direct your request today? If you need to speak with a human expert, just ask to **connect**.")
    
    if st.session_state.meet_loader:
        with st.spinner("Connecting to live consultant session..."):
            time.sleep(2)
        st.session_state.meet_loader = False
        st.session_state.state = 2
        st.session_state.messages = []
        st.rerun()

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    if prompt := st.chat_input("Type your preliminary question...", key="portal_input"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Intercept Keywords
        trigger_words = ["connect", "meet", "expert", "call", "talk"]
        if any(word in prompt.lower() for word in trigger_words):
            st.session_state.meet_loader = True
            st.rerun()
            
        with st.chat_message("user"):
            st.markdown(prompt)
            
        with st.spinner("Analyzing..."):
            try:
                # Compile history for Portal
                ollama_messages = [{'role': 'system', 'content': get_system_instruction()}]
                for m in st.session_state.messages[-5:]:
                    ollama_messages.append({'role': m['role'], 'content': m['content']})
                
                res = ollama.chat(
                    model='llama3.2:1b',
                    messages=ollama_messages,
                    options={'temperature': 0.5, 'repeat_penalty': 1.15}
                )
                ai_reply = res['message']['content'].strip()
            except Exception as e:
                ai_reply = f"[Offline Mode] Unable to connect to inference pipeline. {e}"
                
        with st.chat_message("assistant"):
            st.markdown(ai_reply)
        st.session_state.messages.append({"role": "assistant", "content": ai_reply})
        
        # Layer 3: DB Log
        database.save_chat(f"{profile_choice} (Portal)", prompt, ai_reply)

# =========================================================================
# STATE 2: GOOGLE MEET IMMERSIVE ROOM
# =========================================================================
else:
    st.markdown("<h3 style='color: #E8EAED; font-weight: 600; margin-bottom: 20px; font-family: \"Inter\", sans-serif;'>Live Session Active</h3>", unsafe_allow_html=True)
    
    # Partition the workspace into a 2-column layout row
    col1, col2 = st.columns([4, 6])
    
    # Column 1: Portrait Video Frame
    with col1:
        video_path = os.path.join("static", target_video)
        if os.path.exists(video_path):
            st.video(video_path, autoplay=True, loop=True, muted=True)
        else:
            st.warning(f"Video asset not found: {video_path}")

    # Column 2: Meet Chat Sidebar Panel
    with col2:
        st.markdown("<h4 style='margin-top: 0; color: #E8EAED;'>Meeting Log</h4>", unsafe_allow_html=True)
        log_container = st.container()
        with log_container:
            for msg in st.session_state.messages:
                if msg["role"] == "user":
                    st.markdown(f'<div class="meet-msg-bubble msg-user"><b>You:</b> {msg["content"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="meet-msg-bubble msg-ai"><b>{profile_choice}:</b> {msg["content"]}</div>', unsafe_allow_html=True)
        status_placeholder = st.empty()
    
    # Centralized utility action control belt
    st.markdown('<div class="utility-belt">', unsafe_allow_html=True)
    btn_cols = st.columns(4)
    with btn_cols[0]:
        unmute_speak = st.button("🎙️ Unmute & Speak", use_container_width=True)
    with btn_cols[1]:
        cam_label = "🚫 Turn Off Camera" if st.session_state.camera_on else "📷 Turn On Camera"
        toggle_cam = st.button(cam_label, use_container_width=True)
    with btn_cols[2]:
        pres_label = "⏹️ Stop Presenting" if st.session_state.presenting else "🖥️ Present Screen"
        toggle_pres = st.button(pres_label, use_container_width=True)
    with btn_cols[3]:
        leave_session = st.button("🔴 Leave Session", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    broadcast_query = st.chat_input("Broadcast text to call line...", key="meet_input")

    if toggle_cam:
        st.session_state.camera_on = not st.session_state.camera_on
        state_msg = "Camera turned ON." if st.session_state.camera_on else "Camera turned OFF."
        st.toast(state_msg, icon="📷")
        
    if toggle_pres:
        st.session_state.presenting = not st.session_state.presenting
        state_msg = "You are now presenting your screen." if st.session_state.presenting else "Screen sharing stopped."
        st.toast(state_msg, icon="🖥️")

    if st.session_state.presenting:
        st.info("You are presenting your screen to the meeting.")

    if leave_session:
        st.session_state.state = 1
        st.session_state.messages = []
        st.rerun()

    active_query = None
    if unmute_speak:
        with st.spinner("Listening... Speak now."):
            spoken_text = listen_to_microphone()
            if spoken_text:
                active_query = spoken_text
            else:
                st.warning("No speech detected. Please try again.")

    if broadcast_query:
        active_query = broadcast_query

    # Process query
    if active_query:
        st.session_state.messages.append({"role": "user", "content": active_query})
        
        # Immediately show user's message in the log container so they know it registered
        with log_container:
            st.markdown(f'<div class="meet-msg-bubble msg-user"><b>You:</b> {active_query}</div>', unsafe_allow_html=True)
            
        with status_placeholder:
            with st.spinner("Consultant thinking..."):
                try:
                    # Compile history for Live Room
                    ollama_messages = [{'role': 'system', 'content': get_system_instruction()}]
                    for m in st.session_state.messages[-5:]:
                        ollama_messages.append({'role': m['role'], 'content': m['content']})
                        
                    res = ollama.chat(
                        model='llama3.2:1b',
                        messages=ollama_messages,
                        options={'temperature': 0.5, 'repeat_penalty': 1.15}
                    )
                    ai_response = res['message']['content'].strip()
                except Exception as e:
                    ai_response = f"Connection error: {e}"
        
        st.session_state.messages.append({"role": "assistant", "content": ai_response})
        database.save_chat(f"{profile_choice} (Live Room)", active_query, ai_response)
        st.rerun()