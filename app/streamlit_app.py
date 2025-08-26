import os, json
import pandas as pd
import streamlit as st

import os
# Load API keys from Streamlit secrets
os.environ["TAVILY_API_KEY"] = st.secrets["TAVILY_API_KEY"]
os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]
os.environ["GOOGLE_MODEL"] = st.secrets.get("GOOGLE_MODEL", "gemini-2.0-flash-lite")
os.environ["LLM_PROVIDER"] = st.secrets.get("LLM_PROVIDER", "google")
from dotenv import load_dotenv
from shopsmart.agents import run_pipeline

st.set_page_config(page_title="ShopSmart-EG", page_icon="🛍️", layout="wide")

with st.sidebar:
    st.title("🛍️ ShopSmart-EG")
    st.caption("Amazon.eg • Jumia • Noon (Egypt) — powered by Tavily + LLMs")
    with st.expander("API Keys & Models", expanded=True):
        provider = st.selectbox("LLM Provider", ["openai","anthropic","google"], index=["openai","anthropic","google"].index(os.getenv("LLM_PROVIDER","openai")))
        st.session_state["LLM_PROVIDER"] = provider
        if provider == "openai":
            st.text_input("OPENAI_API_KEY", value=os.getenv("OPENAI_API_KEY",""), type="password", key="OPENAI_API_KEY")
            st.text_input("OPENAI_MODEL", value=os.getenv("OPENAI_MODEL","gpt-4o-mini"), key="OPENAI_MODEL")
        elif provider == "anthropic":
            st.text_input("ANTHROPIC_API_KEY", value=os.getenv("ANTHROPIC_API_KEY",""), type="password", key="ANTHROPIC_API_KEY")
            st.text_input("ANTHROPIC_MODEL", value=os.getenv("ANTHROPIC_MODEL","claude-3-haiku-20240307"), key="ANTHROPIC_MODEL")
        else:
            st.text_input("GOOGLE_API_KEY", value=os.getenv("GOOGLE_API_KEY",""), type="password", key="GOOGLE_API_KEY")
            st.text_input("GOOGLE_MODEL", value=os.getenv("GOOGLE_MODEL","gemini-2.0-flash-lite"), key="GOOGLE_MODEL")
        st.text_input("TAVILY_API_KEY", value=os.getenv("TAVILY_API_KEY",""), type="password", key="TAVILY_API_KEY")
    st.divider()
    budget = st.number_input("Max Budget (EGP)", min_value=0, value=0, step=100)
    min_rating = st.slider("Min Rating", 0.0, 5.0, 0.0, 0.1)
    brand = st.text_input("Preferred Brand (optional)", "")
    features = st.text_input("Must-have features (comma separated)", "")
    st.caption("Note: This app fetches a small number of public pages and follows polite backoff.")

st.title("ShopSmart-EG — Multi Agent Shopping Assistant")
user_query = st.text_input("What are you shopping for today?", placeholder="e.g., wireless earbuds under 2000 EGP with ANC")

if st.button("Search", type="primary") and user_query.strip():
    # Persist keys into env for this process
    os.environ["LLM_PROVIDER"] = st.session_state.get("LLM_PROVIDER","openai")
    for k in ["OPENAI_API_KEY","OPENAI_MODEL","ANTHROPIC_API_KEY","ANTHROPIC_MODEL","GOOGLE_API_KEY","GOOGLE_MODEL","TAVILY_API_KEY"]:
        if k in st.session_state and st.session_state[k]:
            os.environ[k] = st.session_state[k]
    # Compose enriched query
    q = user_query
    if budget:
        q += f" under {budget} EGP"
    if brand:
        q += f" {brand}"
    if features.strip():
        q += " " + features.strip()
    with st.spinner("Thinking with multiple agents..."):
        result = run_pipeline(q)
    st.success("Done!")

    # Results
    plan = result.get("plan", {})
    st.subheader("Search Plan")
    st.json(plan)

    prods = result.get("products", [])
    if prods:
        df = pd.DataFrame(prods)
        show_cols = ["title","price","rating","source","url"]
        st.dataframe(df[show_cols].sort_values(by=["source","price"], na_position="last"), use_container_width=True, hide_index=True)

    top5 = result.get("top5", [])
    if top5:
        st.subheader("Top Candidates")
        df2 = pd.DataFrame(top5)
        st.dataframe(df2[["title","price","rating","source","url"]], use_container_width=True, hide_index=True)

    st.subheader("Summary")
    st.markdown(result.get("summary",""))

    st.subheader("Recommendation")
    st.json(result.get("recommendation", {}))
else:
    st.caption("Enter a query and press **Search**. For best results include budget and desired features.")


from streamlit_webrtc import webrtc_streamer, WebRtcMode
import speech_recognition as sr
import queue

st.subheader("🎤 Voice Input (Optional)")
webrtc_ctx = webrtc_streamer(
    key="speech-to-text",
    mode=WebRtcMode.SENDONLY,
    audio_receiver_size=256,
    media_stream_constraints={"audio": True, "video": False},
    async_processing=True,
)

voice_text = None
if webrtc_ctx.audio_receiver:
    try:
        audio_frames = []
        while not webrtc_ctx.audio_receiver._queue.empty():
            frame = webrtc_ctx.audio_receiver._queue.get_nowait()
            audio_frames.append(frame)
        if audio_frames:
            with open("temp.wav", "wb") as f:
                for frame in audio_frames:
                    f.write(frame.to_ndarray().tobytes())

            recognizer = sr.Recognizer()
            with sr.AudioFile("temp.wav") as source:
                audio = recognizer.record(source)
                voice_text = recognizer.recognize_google(audio, language="en-US")
                st.success(f"You said: {voice_text}")
    except Exception as e:
        st.error(f"Voice input failed: {e}")

query_input = st.text_input("What are you shopping for today?", value=voice_text or "")
