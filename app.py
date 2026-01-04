import streamlit as st
from openai import OpenAI # We still use this library because it's compatible!

st.set_page_config(page_title="The Why Engine (Gemini)", page_icon="🤔")

with st.sidebar:
    st.title("Settings")
    # Change the label so you know it's for Gemini now
    api_key = st.text_input("Gemini API Key", type="password")
    st.info("Using Gemini 2.5 Flash via Google AI Studio.")

if not api_key:
    st.warning("Please enter your Gemini API Key to start.")
    st.stop()

# --- THE MAGIC CHANGE ---
# We tell the app to talk to Google instead of OpenAI
client = OpenAI(
    api_key=api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

def agent_call(role_prompt, user_content):
    response = client.chat.completions.create(
        model="gemini-2.5-flash", # Use Google's fast, free model
        messages=[
            {"role": "system", "content": role_prompt},
            {"role": "user", "content": user_content}
        ],
        temperature=0.7
    )
    return response.choices[0].message.content

# --- UI Setup (Same as before) ---
st.title("🤔 The 'Why' Engine")
topic = st.text_input("Enter a topic:", placeholder="e.g., Why is the sky blue?")

if st.button("Start Investigation"):
    iteration = 1
    consensus = False
    current_answer = agent_call("You are an expert Proposer. Provide a concise answer.", f"Explain: {topic}")
    
    with st.status("Investigating...", expanded=True) as status:
        st.write(f"**Initial Answer:** {current_answer}")
        
        while not consensus and iteration <= 5:
            st.markdown(f"### 🔄 Iteration {iteration}")
            
            # Interrogators
            why_skeptic = agent_call("You are 'The Skeptic'. Ask a piercing 'Why' question.", current_answer)
            why_analyst = agent_call("You are 'The Analyst'. Ask a 'Why' question focusing on first principles.", current_answer)
            
            st.info(f"**Skeptic:** {why_skeptic}")
            st.info(f"**Analyst:** {why_analyst}")
            
            # Check for Consensus
            decision = agent_call("If the answer is fundamental, reply 'AGREE'. Otherwise, 'CONTINUE'.", f"Answer: {current_answer}")
            
            if "AGREE" in decision.upper():
                consensus = True
                status.update(label="✅ Root Cause Found!", state="complete")
            else:
                iteration += 1
                current_answer = agent_call("Incorporate these 'Whys' into a deeper answer.", f"Old: {current_answer}\nQuestions: {why_skeptic}, {why_analyst}")
                st.write(f"**Refined Answer:** {current_answer}")

    st.success(f"Final Truth: {current_answer}")
