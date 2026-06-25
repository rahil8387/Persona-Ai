# 🎭 Persona AI Studio

A full-stack, cloud-to-local AI platform that allows users to interact with unique virtual personas powered by a locally hosted **Llama 3.2** LLM. The frontend is fully deployed to the cloud, communicating securely with a high-performance local backend via SSH tunneling.

---

## 🚀 Key Features
* **Dynamic Persona Selection:** Instantly switch between custom AI personalities (e.g., Technical Interviewer, Data Scientist, Supportive Mentor).
* **Cloud-to-Local Bridge:** Hosted serverless frontend communicating directly with local consumer hardware using secure SSH edge tunnels.
* **Asynchronous Streaming UI:** Beautiful, dark-themed responsive chat interface designed for low latency.
* **Local Privacy First:** Full AI inference runs entirely on the local machine keeping data safe and offline.

---

## 🛠️ The Tech Stack

| Layer | Technology Used | Description |
| :--- | :--- | :--- |
| **Frontend** | HTML5, CSS3, JavaScript (ES6) | Responsive UI with clean animations, deployed on **Vercel**. |
| **Backend** | Python, FastAPI, Uvicorn | High-performance, asynchronous REST API endpoints. |
| **AI Engine** | Ollama, Llama 3.2 (3B) | Local Large Language Model running advanced inference. |
| **Tunneling** | Localhost.run / SSH | Secure reverse proxy forwarding cloud traffic to `localhost:8000`. |

---

## 📐 System Architecture

1. **User** opens the live cloud website deployed on **Vercel**.
2. **Frontend JavaScript** fires an asynchronous `POST` fetch request containing the message and selected persona.
3. Traffic passes securely through an active **SSH Reverse Proxy Tunnel** directly to the local development machine.
4. **FastAPI Backend** intercepts the payload, formats the prompt template, and sends it to **Ollama (Llama 3.2)**.
5. **AI Inference** processes the request locally and bounces the structured response back up the chain to the cloud UI.

---

## 📦 How to Run Locally

### 1. Prerequisites
Ensure you have Python installed and **Ollama** running with Llama 3.2:
```bash
ollama run llama3.2