import streamlit as st
import time
import json

# Constants
TIMER_SECONDS = 10  # Time per question in timer mode
QUESTIONS = [
    {"question": "What is the capital of France?", "options": ["Berlin", "Madrid", "Paris", "Rome"]},
    {"question": "Which language is primarily spoken in Brazil?", "options": ["Portuguese", "Spanish", "English", "French"]},
    {"question": "What is 5 + 7?", "options": ["10", "11", "12", "13"]},
]

# Session state initialization
if 'mode' not in st.session_state:
    st.session_state.mode = "timer"  # "timer" or "relaxed"
if 'answers' not in st.session_state:
    st.session_state.answers = {"timer": [], "relaxed": []}
if 'question_index' not in st.session_state:
    st.session_state.question_index = 0
if 'start_time' not in st.session_state:
    st.session_state.start_time = None
if 'relaxed_times' not in st.session_state:
    st.session_state.relaxed_times = []

# Timer mode
if st.session_state.mode == "timer":
    st.title("Survey - Timer Mode")
    question = QUESTIONS[st.session_state.question_index]
    
    st.write(question["question"])
    selected = st.radio("Select an answer:", question["options"], key=f"timer_{st.session_state.question_index}")
    
    # Progress bar countdown
    progress_bar = st.progress(100)
    for remaining_time in range(TIMER_SECONDS, 0, -1):
        time.sleep(1)
        progress_bar.progress(int((remaining_time / TIMER_SECONDS) * 100))
    
    # Save answer and go to next question
    st.session_state.answers["timer"].append(selected)
    st.session_state.question_index += 1
    
    if st.session_state.question_index >= len(QUESTIONS):
        st.session_state.mode = "relaxed"  # Switch mode
        st.session_state.question_index = 0  # Reset index
        st.experimental_rerun()

# Relaxed mode
elif st.session_state.mode == "relaxed":
    st.title("Survey - Relaxed Mode")
    
    question = QUESTIONS[st.session_state.question_index]
    st.write(question["question"])
    
    if st.session_state.start_time is None:
        st.session_state.start_time = time.time()
    
    selected = st.radio("Select an answer:", question["options"], key=f"relaxed_{st.session_state.question_index}")
    
    if st.button("Next"):
        elapsed_time = time.time() - st.session_state.start_time
        st.session_state.relaxed_times.append(elapsed_time)
        st.session_state.answers["relaxed"].append(selected)
        st.session_state.start_time = None
        
        if st.session_state.question_index < len(QUESTIONS) - 1:
            st.session_state.question_index += 1
        else:
            st.write("Survey completed! Thanks for participating.")
            st.json(st.session_state.answers)
            st.stop()
        st.experimental_rerun()
    
    if st.session_state.question_index > 0 and st.button("Previous"):
        st.session_state.question_index -= 1
        st.session_state.start_time = None
        st.experimental_rerun()
