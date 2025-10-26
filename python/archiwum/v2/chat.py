import streamlit as st
import time
import json

# Define questions
QUESTIONS = [
    "What is your favorite color?",
    "What is your favorite food?",
    "What is your dream job?",
    "Where would you like to travel?"
]

def main():
    st.title("Survey Application")
    
    # Session state to keep track of answers and mode
    if "mode" not in st.session_state:
        st.session_state.mode = "timer"
        st.session_state.answers = {}
        st.session_state.timer_expired = False
        st.session_state.relaxed_times = {}
        st.session_state.current_question = 0
        st.session_state.start_time = None
    
    if st.session_state.mode == "timer":
        timer_mode()
    else:
        relaxed_mode()

def timer_mode():
    st.header("Timer Mode")
    question_idx = st.session_state.current_question
    if question_idx >= len(QUESTIONS):
        st.session_state.mode = "relaxed"
        st.session_state.current_question = 0
        st.experimental_rerun()
    
    st.subheader(f"Question {question_idx + 1}: {QUESTIONS[question_idx]}")
    
    # Timer countdown
    timer_duration = 10  # 10 seconds per question
    if "start_time" not in st.session_state or st.session_state.start_time is None:
        st.session_state.start_time = time.time()
    
    time_left = timer_duration - (time.time() - st.session_state.start_time)
    progress = max(0, time_left / timer_duration)
    st.progress(progress)
    
    if time_left <= 0:
        st.session_state.timer_expired = True
    
    answer = st.text_input("Your answer:", key=f"timer_q{question_idx}")
    if st.button("Next") or st.session_state.timer_expired:
        st.session_state.answers[question_idx] = answer
        st.session_state.current_question += 1
        st.session_state.start_time = None
        st.session_state.timer_expired = False
        st.experimental_rerun()

def relaxed_mode():
    st.header("Relaxed Mode")
    question_idx = st.session_state.current_question
    
    if question_idx >= len(QUESTIONS):
        st.write("Survey completed! Thank you for your answers.")
        st.json(st.session_state.answers)
        st.stop()
    
    st.subheader(f"Question {question_idx + 1}: {QUESTIONS[question_idx]}")
    
    # Track time spent per question
    if question_idx not in st.session_state.relaxed_times:
        st.session_state.relaxed_times[question_idx] = time.time()
    
    answer = st.text_input("Your answer:", value=st.session_state.answers.get(question_idx, ""), key=f"relaxed_q{question_idx}")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Previous") and question_idx > 0:
            st.session_state.answers[question_idx] = answer
            st.session_state.relaxed_times[question_idx] = time.time() - st.session_state.relaxed_times[question_idx]
            st.session_state.current_question -= 1
            st.experimental_rerun()
    
    with col2:
        if st.button("Next"):
            st.session_state.answers[question_idx] = answer
            st.session_state.relaxed_times[question_idx] = time.time() - st.session_state.relaxed_times[question_idx]
            st.session_state.current_question += 1
            st.experimental_rerun()

if __name__ == "__main__":
    main()
