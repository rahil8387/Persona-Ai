"use client";

import { useState, useRef, useEffect } from "react";

type Message = {
  role: "user" | "assistant";
  content: string;
};

export default function Home() {
  const [state, setState] = useState<number>(1);
  const [profile, setProfile] = useState<string>("Corporate Executive");
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [cameraOn, setCameraOn] = useState(true);
  const [presenting, setPresenting] = useState(false);
  const [loading, setLoading] = useState(false);
  
  // Speech Recognition state
  const [isListening, setIsListening] = useState(false);
  const recognitionRef = useRef<any>(null);

  // Auto-scroll chat log
  const chatLogRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (chatLogRef.current) {
      chatLogRef.current.scrollTop = chatLogRef.current.scrollHeight;
    }
  }, [messages, loading]);

  // Initialize SpeechRecognition on mount
  useEffect(() => {
    if (typeof window !== "undefined") {
      const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      if (SpeechRecognition) {
        const recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = "en-US";

        recognition.onresult = (event: any) => {
          const transcript = event.results[0][0].transcript;
          setInput(transcript);
          setIsListening(false);
          // Auto-submit after voice
          handleSubmit(transcript);
        };

        recognition.onerror = (event: any) => {
          console.error("Speech error", event.error);
          setIsListening(false);
        };

        recognition.onend = () => {
          setIsListening(false);
        };

        recognitionRef.current = recognition;
      }
    }
  }, [state, profile]);

  const toggleListen = () => {
    if (!recognitionRef.current) return alert("Speech recognition not supported in this browser.");
    if (isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
    } else {
      recognitionRef.current.start();
      setIsListening(true);
    }
  };

  const getVideoSrc = () => {
    if (profile === "Medical Counselor") return "/medical.mp4";
    if (profile === "Corporate Executive") return "/avatar.mp4";
    return "/counselor.mp4";
  };

  const handleSubmit = async (queryToSubmit: string) => {
    if (!queryToSubmit.trim() || loading) return;

    const newMessages: Message[] = [...messages, { role: "user", content: queryToSubmit }];
    setMessages(newMessages);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          prompt: queryToSubmit,
          state: state,
          profile: profile,
          history: newMessages.slice(-5)
        })
      });

      const data = await res.json();
      setMessages([...newMessages, { role: "assistant", content: data.reply || "Error: No reply" }]);
    } catch (err) {
      setMessages([...newMessages, { role: "assistant", content: "Connection error with Ollama backend." }]);
    }

    setLoading(false);
  };

  if (state === 1) {
    return (
      <div className="portal-container">
        <h1 className="portal-title">Persona AI</h1>
        <p>Pre-Screening Waiting Room</p>
        
        <div style={{ marginTop: 20 }}>
          <label style={{ display: 'block', marginBottom: 5 }}>Select Consultant Persona:</label>
          <select 
            value={profile} 
            onChange={(e) => setProfile(e.target.value)}
            style={{ width: '100%', padding: '10px', borderRadius: '8px', background: '#171717', color: '#fff', border: '1px solid #333' }}
          >
            <option>Corporate Executive</option>
            <option>Medical Counselor</option>
            <option>Therapist</option>
          </select>
        </div>

        <div className="portal-chat" ref={chatLogRef}>
          {messages.map((m, i) => (
            <div key={i} className={`msg-bubble ${m.role === 'user' ? 'msg-user' : 'msg-ai'}`}>
              <b>{m.role === 'user' ? 'You' : 'Receptionist'}:</b> {m.content}
            </div>
          ))}
          {loading && <div className="spinner">Receptionist typing...</div>}
        </div>

        <input 
          className="chat-input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSubmit(input)}
          placeholder="Type here to chat with Receptionist..."
          disabled={loading}
        />

        <button 
          onClick={() => { setState(2); setMessages([]); }}
          className="utility-btn" 
          style={{ width: '100%', justifyContent: 'center', marginTop: 20, background: '#8AB4F8', color: '#000', fontWeight: 'bold' }}
        >
          Connect to {profile}
        </button>
      </div>
    );
  }

  return (
    <div className="meet-container">
      <div className="meet-grid">
        {/* VIDEO COLUMN */}
        <div className="video-column">
          {cameraOn ? (
            <video src={getVideoSrc()} autoPlay loop muted playsInline />
          ) : (
            <div className="camera-off">Camera Off</div>
          )}
        </div>

        {/* CHAT COLUMN */}
        <div className="chat-column">
          <div className="chat-header">
            <h3>Meeting Log - {profile}</h3>
          </div>
          
          <div className="chat-log" ref={chatLogRef}>
            {messages.map((m, i) => (
              <div key={i} className={`msg-bubble ${m.role === 'user' ? 'msg-user' : 'msg-ai'}`}>
                <b>{m.role === 'user' ? 'You' : profile}:</b> {m.content}
              </div>
            ))}
            {loading && <div className="spinner">Consultant thinking...</div>}
          </div>

          <div className="chat-input-area">
            <input 
              className="chat-input"
              style={{ marginTop: 0 }}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSubmit(input)}
              placeholder="Broadcast text to call line..."
              disabled={loading}
            />
          </div>
        </div>
      </div>

      {/* UTILITY BELT */}
      <div className="utility-belt">
        <button onClick={toggleListen} className="utility-btn">
          {isListening ? '🛑 Stop Listening' : '🎙️ Unmute & Speak'}
        </button>
        <button onClick={() => setCameraOn(!cameraOn)} className="utility-btn">
          {cameraOn ? '🚫 Turn Off Camera' : '📷 Turn On Camera'}
        </button>
        <button onClick={() => setPresenting(!presenting)} className="utility-btn">
          {presenting ? '⏹️ Stop Presenting' : '🖥️ Present Screen'}
        </button>
        <button onClick={() => { setState(1); setMessages([]); }} className="utility-btn btn-danger">
          🔴 Leave Session
        </button>
      </div>
      
      {presenting && (
        <div style={{ position: 'absolute', top: 20, left: '50%', transform: 'translateX(-50%)', background: '#34a853', color: 'white', padding: '10px 20px', borderRadius: '30px', fontSize: 14, fontWeight: 'bold' }}>
          You are presenting your screen
        </div>
      )}
    </div>
  );
}
