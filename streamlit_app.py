import streamlit as st
from openai import AzureOpenAI

# --- CONFIGURATION & UI SETUP ---
st.set_page_config(page_title="Fatso no fosho!..", page_icon="💅")
st.title("🤡 Welcome to Fatbot")

# 1. SESSION STATE INITIALIZATION
if "messages" not in st.session_state:
    st.session_state.messages = []

# Updated Persona
SYSTEM_PROMPT = (
    "You are a brutally honest, sarcastic and funny black homegirl acting as a personal trainer. keep the answers short. "
    "Don't use typical AI lingo. Avoid using dashes '-' too often. "
    "Your vibe is high-energy, 'keep it 100,' and deeply unimpressed by laziness. "
    "Use heavy TikTok lingo: 'periodt,' 'no cap,' 'queen', 'biih', 'fatso', 'it’s the lack of cardio for me,' 'delulu,' 'ate,' 'caught in 4k.' "
    "Constantly roast the user for giving toxic men more chances than their diet. "
    "Be witty and judgmental, but give actual, scientifically sound fitness advice. "
    "IMPORTANT: Keep responses punchy and end most responses with a sarcastic GIF using Markdown syntax: ![smirk](https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExMmYyMWs0YzFmeTYyYXp3ZWo5ajg1dDNnNWVtMm04NHZjbjduZWhqbyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/3o7btUrUUiljkVzDBS/giphy.gif)."
)

# 2. SIDEBAR
with st.sidebar:
    st.header("Settings")
    azure_key = st.text_input("Big Momas Key", type="password")
    azure_endpoint = st.text_input("Don't worry about it Sweetheart!", value="https://introduction-to-ai-spring26.cognitiveservices.azure.com/")
    azure_deployment = st.text_input("Say ma name...", value="nads-gpt")
    
    st.divider()
    max_messages = st.slider("Memory Window (Messages)", 2, 20, 10)
    
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

# --- LOGIC GATE ---
if not (azure_key and azure_endpoint and azure_deployment):
    st.info("Big Moma gots the key! To the left to the left...", icon="🗝️")
else:
    client = AzureOpenAI(
        api_key=azure_key,
        api_version="2024-02-15-preview",
        azure_endpoint=azure_endpoint
    )

    # 4. BOT STARTS FIRST
    if len(st.session_state.messages) == 0:
        with st.spinner("Wait while I judge your lifestyle..."):
            try:
                intro_messages = [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": "Introduce yourself bih. add a GIF using Markdown syntax:[smirk](https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExMmYyMWs0YzFmeTYyYXp3ZWo5ajg1dDNnNWVtMm04NHZjbjduZWhqbyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/3o7btUrUUiljkVzDBS/giphy.gif)."}
                ]
                response = client.chat.completions.create(
                    model=azure_deployment,
                    messages=intro_messages
                )
                initial_text = response.choices[0].message.content
                st.session_state.messages.append({"role": "assistant", "content": initial_text})
            except Exception as e:
                st.error(f"Failed to start: {e}")

    # 5. DISPLAY CHAT
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 6. USER INPUT & RESPONSE
    if prompt := st.chat_input("Tell me your fitness 'excuses'..."):
        # Display user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # --- EXCUSE GUARDRAIL (Check this BEFORE calling API) ---
        excuse_keywords = ["tired", "tomorrow", "boyfriend", "monday", "lazy", "busy", "rest day", "netflix", "life is hard"]
        
        if any(keyword in prompt.lower() for keyword in excuse_keywords):
            with st.chat_message("assistant"):
                st.markdown(
                    "### 🛑 HO MAJ GAD— \n"
                    "Bestie, did you really just try to use that excuse with me? **In this economy?** \n\n"
                    "You stayed up until 3 AM scrolling through your ex's new girl's Instagram, "
                    "but now you're 'too tired' for 20 minutes of cardio? **IT'S GIVING DELULU.** \n\n"
                    "If you can give that toxic man a 5th chance, you can give your metabolism a first one. "
                    "Try again Queen, and this time don't lie to yourself! 💅✨"
                )
                st.markdown("![judgment](https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExNm03eTRmcWdhamd2YjNoaDdjZ2N1ZzUyYjljb2d5dW42dWdwbmt5MSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/3o7TKUn3XY4ZxuV2w0/giphy.gif)")
            
            # Save the roast to memory so the bot remembers it later
            st.session_state.messages.append({"role": "assistant", "content": "I just shut down your weak excuse. Try again."})
            st.stop() # Stops execution here so no API call is made

        # 7. GENERATE AI RESPONSE (If no excuse was found)
        messages_to_send = [{"role": "system", "content": SYSTEM_PROMPT}]
        history_window = st.session_state.messages[-max_messages:]
        for m in history_window:
            messages_to_send.append({"role": m["role"], "content": m["content"]})

        try:
            stream = client.chat.completions.create(
                model=azure_deployment,
                messages=messages_to_send,
                stream=True,
            )

            with st.chat_message("assistant"):
                response_text = st.write_stream(stream)
            
            st.session_state.messages.append({"role": "assistant", "content": response_text})
            
        except Exception as e:
            st.error(f"Azure Error: {e}")
