import streamlit as st
import time

# --- Constants ---
TIMER_SECONDS = 10
QUESTIONS = [
    {"question": "What is the capital of France?", "options": ["Berlin", "Madrid", "Paris", "Rome"]},
    {"question": "Which language is primarily spoken in Brazil?", "options": ["Portuguese", "Spanish", "English", "French"]},
    {"question": "What is 5 + 7?", "options": ["10", "11", "12", "13"]},
]

# --- Session State Initialization ---
if "mode" not in st.session_state:
    st.session_state.mode = "timer"  # "timer" or "relaxed"
if "answers" not in st.session_state:
    st.session_state.answers = {"timer": [], "relaxed": []}
if "question_index" not in st.session_state:
    st.session_state.question_index = 0
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "times" not in st.session_state:
    st.session_state.times = {"timer": [], "relaxed": []}

def go_to_next_question():
    st.session_state.question_index += 1
    st.session_state.start_time = None
    st.experimental_rerun()

# --- Timer Mode ---
def timer_mode():
    st.title("Survey - Timer Mode")
    q_idx = st.session_state.question_index
    question = QUESTIONS[q_idx]

    st.write(question["question"])
    radio_key = f"timer_{q_idx}"
    selected = st.radio("Select an answer:", question["options"], key=radio_key)

    if st.session_state.start_time is None:
        st.session_state.start_time = time.time()

    progress_placeholder = st.empty()
    for t in range(TIMER_SECONDS, 0, -1):
        progress_placeholder.progress(t / TIMER_SECONDS)
        time.sleep(1)

    # Save answer (None if unanswered)
    st.session_state.answers["timer"].append(selected if selected else None)
    elapsed = time.time() - st.session_state.start_time
    st.session_state.times["timer"].append(round(elapsed, 2))

    if q_idx + 1 < len(QUESTIONS):
        go_to_next_question()
    else:
        # Switch to relaxed mode
        st.session_state.mode = "relaxed"
        st.session_state.question_index = 0
        st.session_state.start_time = None
        st.experimental_rerun()

# --- Relaxed Mode ---
def relaxed_mode():
    st.title("Survey - Relaxed Mode")
    q_idx = st.session_state.question_index
    question = QUESTIONS[q_idx]

    st.write(question["question"])
    if st.session_state.start_time is None:
        st.session_state.start_time = time.time()

    selected = st.radio("Select an answer:", question["options"], key=f"relaxed_{q_idx}")

    col1, col2 = st.columns([1, 1])
    if col1.button("Previous") and q_idx > 0:
        st.session_state.question_index -= 1
        st.session_state.start_time = None
        st.experimental_rerun()

    if col2.button("Next"):
        elapsed = time.time() - st.session_state.start_time
        if len(st.session_state.answers["relaxed"]) > q_idx:
            st.session_state.answers["relaxed"][q_idx] = selected
            st.session_state.times["relaxed"][q_idx] = round(elapsed, 2)
        else:
            st.session_state.answers["relaxed"].append(selected)
            st.session_state.times["relaxed"].append(round(elapsed, 2))

        if q_idx + 1 < len(QUESTIONS):
            go_to_next_question()
        else:
            show_results()

def show_results():
    st.title("Survey Completed")
    st.subheader("Your Answers:")
    st.write("Timer Mode:")
    for i, (ans, time_spent) in enumerate(zip(st.session_state.answers["timer"], st.session_state.times["timer"])):
        st.write(f"Q{i+1}: {ans} (Time: {time_spent}s)")

    st.write("Relaxed Mode:")
    for i, (ans, time_spent) in enumerate(zip(st.session_state.answers["relaxed"], st.session_state.times["relaxed"])):
        st.write(f"Q{i+1}: {ans} (Time: {time_spent}s)")

    st.success("Thank you for completing the survey!")
    st.stop()

# --- Main Control ---
if st.session_state.mode == "timer":
    timer_mode()
elif st.session_state.mode == "relaxed":
    relaxed_mode()
