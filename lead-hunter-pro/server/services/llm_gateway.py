import os
import json
import asyncio
import google.generativeai as genai
from groq import Groq

#   Load Config  
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GROQ_API_KEY   = os.getenv("GROQ_API_KEY", "")

#   Initialize Clients  
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    _gemini_model = genai.GenerativeModel("gemini-1.5-flash")
else:
    _gemini_model = None

_groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

async def call_llm(
    prompt: str, 
    expect_json: bool = False, 
    system_message: str = "", 
    gemini_key: str = None, 
    groq_key: str = None
) -> str:
    """
    Unified LLM call: Gemini 1.5 Flash -> Fallback to Groq Llama3.1-8b.
    Explicitly supports per-request BYOK keys.
    """
    #   Attempt 1: Gemini  
    # Priority 1: User-provided key via header; Priority 2: In-memory model config (.env)
    g_key = gemini_key or os.getenv("GEMINI_API_KEY")
    
    if g_key:
        try:
            # Respect Gemini free tier RPM (15 RPM -> ~4s delay)
            await asyncio.sleep(1) 
            
            # Re-configure or use dedicated client if key is different (for BYOK)
            # In a high-traffic env, we'd cache these model objects by key
            genai.configure(api_key=g_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            
            response = await asyncio.to_thread(model.generate_content, prompt)
            return response.text.strip()
        except Exception as e:
            print(f"  [LLMGateway]   Gemini failed: {e}. Falling back to Groq...")

    #   Attempt 2: Groq Fallback  
    gr_key = groq_key or os.getenv("GROQ_API_KEY")
    if gr_key:
        try:
            client = Groq(api_key=gr_key)
            messages = []
            if system_message:
                messages.append({"role": "system", "content": system_message})
            messages.append({"role": "user", "content": prompt})

            response = await asyncio.to_thread(
                client.chat.completions.create,
                model="llama-3.1-8b-instant",
                messages=messages,
                temperature=0.1,
                response_format={"type": "json_object"} if expect_json else None
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"  [LLMGateway]   Groq also failed: {e}")
            raise e
    
    raise Exception("No LLM providers available or configured. Please set GEMINI_API_KEY/GROQ_API_KEY or provide one via headers.")
