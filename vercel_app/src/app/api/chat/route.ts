import { NextResponse } from 'next/server';

export async function POST(req: Request) {
  try {
    const { prompt, state, profile, history } = await req.json();

    let systemInstruction = "";
    
    if (state === 1) {
      systemInstruction = 
        "You are a warm, polite, and welcoming human receptionist. " +
        "If the user says hello, greetings, or asks who you are/how you can help, reply politely in a relaxed way to make them feel comfortable. " +
        "Let them know you can help connect them to an expert consultant. " +
        "If the user asks to connect, meet, call, talk, or requests an expert, confirm warmly that you are transferring them right now. " +
        "Always respond directly to the user's actual prompt. Do not repeat what the user said. " +
        "By default, speak in natural, flowing conversational sentences without bullet points. However, if the user explicitly asks for a chart, list, or structured format, you must provide it.";
    } else {
      systemInstruction = 
        `You are a warm, polite, and highly knowledgeable ${profile} on a live video call. ` +
        "You speak naturally, like a real human in a relaxed, friendly setting. " +
        "If the user greets you or asks who you are, introduce yourself warmly. " +
        "Always pay close attention to the user's prompt and give an accurate, helpful response. " +
        "Keep your answers concise and conversational, as they are being spoken out loud. Do not repeat what the user said. " +
        "CRITICAL RULE: By default, speak ONLY in short, continuous, natural conversational paragraphs without bullet points. HOWEVER, if the user explicitly asks for a chart, table, list, or structured layout, you MUST provide it exactly as requested.";
    }

    const ollamaMessages = [
      { role: "system", content: systemInstruction },
      ...history.map((m: any) => ({ role: m.role, content: m.content })),
      { role: "user", content: prompt }
    ];

    const response = await fetch('http://127.0.0.1:11434/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: 'llama3.2:1b',
        messages: ollamaMessages,
        stream: false,
        options: {
          temperature: 0.5,
          repeat_penalty: 1.15
        }
      })
    });

    if (!response.ok) {
      throw new Error(`Ollama returned status ${response.status}`);
    }

    const data = await response.json();
    return NextResponse.json({ reply: data.message.content.trim() });
    
  } catch (error: any) {
    console.error("Chat API Error:", error);
    return NextResponse.json(
      { reply: "Backend connection error. Make sure Ollama is running locally on port 11434." },
      { status: 500 }
    );
  }
}
