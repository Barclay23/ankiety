import streamlit as st
import time
import pandas as pd
from datetime import datetime

# Configuration
st.set_page_config(page_title="Survey App", layout="wide")

# Survey questions
QUESTIONS = [
    {
        "question": "How often do you use Python for your work?",
        "options": ["Daily", "Weekly", "Monthly", "Rarely", "Never"]
    },
    {
        "question": "How would you rate your Python expertise?",
        "options": ["Beginner", "Intermediate", "Advanced", "Expert"]
    },
    {
        "question": "Which Python web framework do you prefer?",
        "options": ["Django", "Flask", "FastAPI", "Streamlit", "Other"]
    }
]

# Session state initialization
if 'mode' not in st.session_state:
    st.session_state.mode = None
if 'current_question' not in st.session_state:
    st.session_state.current_question = 0
if 'timer_start' not in st.session_state:
    st.session_state.timer_start = None
if 'answers_timer' not in st.session_state:
    st.session_state.answers_timer = {}
if 'answers_relaxed' not in st.session_state:
    st.session_state.answers_relaxed = {}
if 'time_spent_relaxed' not in st.session_state:
    st.session_state.time_spent_relaxed = {}
if 'question_start_time' not in st.session_state:
    st.session_state.question_start_time = None

# Constants
TIMER_DURATION = 15  # seconds per question in timer mode

def reset_timer():
    st.session_state.timer_start = time.time()

def start_timer_mode():
    st.session_state.mode = "timer"
    st.session_state.current_question = 0
    st.session_state.answers_timer = {}
    reset_timer()

def start_relaxed_mode():
    st.session_state.mode = "relaxed"
    st.session_state.current_question = 0
    st.session_state.answers_relaxed = {}
    st.session_state.time_spent_relaxed = {}
    st.session_state.question_start_time = time.time()

def next_question():
    if st.session_state.mode == "timer":
        st.session_state.answers_timer[st.session_state.current_question] = st.session_state.get(
            f"answer_{st.session_state.current_question}", "No answer")
    elif st.session_state.mode == "relaxed":
        end_time = time.time()
        time_spent = end_time - st.session_state.question_start_time
        st.session_state.time_spent_relaxed[st.session_state.current_question] = time_spent
        st.session_state.answers_relaxed[st.session_state.current_question] = st.session_state.get(
            f"answer_{st.session_state.current_question}", "No answer")
        st.session_state.question_start_time = time.time()
    
    if st.session_state.current_question < len(QUESTIONS) - 1:
        st.session_state.current_question += 1
        if st.session_state.mode == "timer":
            reset_timer()
    else:
        if st.session_state.mode == "timer":
            start_relaxed_mode()
        else:
            st.session_state.mode = "completed"

def prev_question():
    if st.session_state.mode == "relaxed" and st.session_state.current_question > 0:
        end_time = time.time()
        time_spent = end_time - st.session_state.question_start_time
        st.session_state.time_spent_relaxed[st.session_state.current_question] = time_spent
        st.session_state.answers_relaxed[st.session_state.current_question] = st.session_state.get(
            f"answer_{st.session_state.current_question}", "No answer")
        
        st.session_state.current_question -= 1
        st.session_state.question_start_time = time.time()

def render_question():
    question_data = QUESTIONS[st.session_state.current_question]
    
    if st.session_state.mode == "timer":
        elapsed = time.time() - st.session_state.timer_start
        remaining = max(0, TIMER_DURATION - elapsed)
        progress = remaining / TIMER_DURATION
        
        # Update the progress bar
        timer_bar.progress(progress)
        
        # Display remaining time
        st.subheader(f"Time remaining: {int(remaining)} seconds")
        
        # Automatically move to next question when time is up
        if remaining <= 0:
            next_question()
            st.experimental_rerun()
    
    st.subheader(question_data["question"])
    
    # Store the answer in session state
    st.radio(
        "Select your answer:",
        options=question_data["options"],
        key=f"answer_{st.session_state.current_question}",
        index=None
    )
    
    # Display navigation buttons based on mode
    if st.session_state.mode == "timer":
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("Next", on_click=next_question):
                pass
    elif st.session_state.mode == "relaxed":
        col1, col2, col3 = st.columns([1, 1, 3])
        with col1:
            if st.session_state.current_question > 0:
                if st.button("Previous", on_click=prev_question):
                    pass
        with col2:
            if st.session_state.current_question < len(QUESTIONS) - 1:
                if st.button("Next", on_click=next_question):
                    pass
            else:
                if st.button("Complete Survey", on_click=next_question):
                    pass

def show_results():
    st.title("Survey Results")
    
    st.subheader("Timer Mode Answers")
    timer_results = []
    for i, question_data in enumerate(QUESTIONS):
        timer_results.append({
            "Question": question_data["question"],
            "Answer": st.session_state.answers_timer.get(i, "No answer")
        })
    st.table(pd.DataFrame(timer_results))
    
    st.subheader("Relaxed Mode Answers")
    relaxed_results = []
    for i, question_data in enumerate(QUESTIONS):
        relaxed_results.append({
            "Question": question_data["question"],
            "Answer": st.session_state.answers_relaxed.get(i, "No answer"),
            "Time Spent (seconds)": round(st.session_state.time_spent_relaxed.get(i, 0), 2)
        })
    st.table(pd.DataFrame(relaxed_results))
    
    if st.button("Start New Survey"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.experimental_rerun()

# Main app logic
st.title("Survey Application")

if st.session_state.mode is None:
    st.write("""
    Welcome to the survey application. Please select a mode to begin:
    - **Timer Mode**: Answer questions with a time limit
    - **Relaxed Mode**: Answer questions at your own pace (available after completing Timer Mode)
    """)
    
    col1, col2 = st.columns(2)
    with col1:
        st.button("Start Timer Mode", on_click=start_timer_mode)
    with col2:
        st.button("Start Relaxed Mode", disabled=True)

elif st.session_state.mode in ["timer", "relaxed"]:
    if st.session_state.mode == "timer":
        timer_bar = st.progress(1.0)
    
    render_question()
    
    if st.session_state.mode == "relaxed":
        st.write("You can now take your time and go back to previous questions if needed.")

elif st.session_state.mode == "completed":
    show_results()