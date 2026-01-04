import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="The Why Engine", page_icon="🤔")

# Sidebar for API Key
with st.sidebar:
    st.title("Settings")
    api_key = st.text_input("OpenAI API Key", type="password")
    st.info("This app uses GPT-4o to simulate 3 agents questioning a topic until they reach first principles.")

if not api_key:
    st.warning("Please enter your OpenAI API Key to start.")
    st.stop()

client = OpenAI(api_key=api_key)

# --- Agent Logic ---
def agent_call(role_prompt, user_content):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": role_prompt},
            {"role": "user", "content": user_content}
        ],
        temperature=0.7
    )
    return response.choices[0].message.content

# --- UI Setup ---
st.title("🤔 The 'Why' Engine")
st.caption("A multi-agent system that drills down to the root cause.")

topic = st.text_input("Enter a topic or claim to investigate:", placeholder="e.g., Why do we use salt on icy roads?")

if st.button("Start Investigation"):
    iteration = 1
    max_iterations = 5
    consensus = False
    
    # 1. Initial Answer
    with st.status("Proposer generating initial answer...", expanded=True) as status:
        current_answer = agent_call("You are an expert Proposer. Provide a concise, clear answer.", f"Explain: {topic}")
        st.write(f"**Initial Answer:** {current_answer}")
        
        while not consensus and iteration <= max_iterations:
            st.markdown(f"### 🔄 Iteration {iteration}")
            
            # 2. Interrogators
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("🕵️ The Skeptic")
                why_skeptic = agent_call("You are 'The Skeptic'. Ask a short, piercing 'Why' question focusing on logical gaps.", current_answer)
                st.info(why_skeptic)
                
            with col2:
                st.subheader("🧐 The Analyst")
                why_analyst = agent_call("You are 'The Analyst'. Ask a short 'Why' question focusing on first principles and physics/human nature.", current_answer)
                st.info(why_analyst)
            
            # 3. Consensus Check
            decision = agent_call(
                "You are the Judge. If the answer is fundamental and leaves no more room for 'Why', reply 'AGREE'. Otherwise, reply 'CONTINUE'.",
                f"Current Answer: {current_answer}\nQuestions: {why_skeptic}, {why_analyst}"
            )
            
            if "AGREE" in decision.upper():
                consensus = True
                status.update(label="✅ Consensus Reached!", state="complete")
                st.success("The agents have agreed upon a fundamental root cause.")
            else:
                iteration += 1
                current_answer = agent_call(
                    "You are the Proposer. Refine your answer to be more fundamental by addressing the two 'Why' questions provided.",
                    f"Old Answer: {current_answer}\nQuestions: {why_skeptic}, {why_analyst}"
                )
                st.write(f"**Refined Answer:** {current_answer}")

    st.balloons()
    st.markdown("---")
    st.subheader("Final Agreed-Upon Truth:")
    st.write(current_answer)