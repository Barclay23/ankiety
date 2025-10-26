import streamlit as st
import time
import json

def load_questions():
    return [
        {"question": "What is the capital of France?", "options": ["Paris", "London", "Berlin", "Madrid"]},
        {"question": "Which programming language is this app written in?", "options": ["Python", "Java", "C++", "JavaScript"]},
        {"question": "What is 2 + 2?", "options": ["3", "4", "5", "6"]}
    ]

def init_session_state():
    if "mode" not in st.session_state:
        st.session_state.mode = "timer"
    if "question_index" not in st.session_state:
        st.session_state.question_index = 0
    if "timer_responses" not in st.session_state:
        st.session_state.timer_responses = {}
    if "relaxed_responses" not in st.session_state:
        st.session_state.relaxed_responses = {}
    if "time_spent_relaxed" not in st.session_state:
        st.session_state.time_spent_relaxed = {}
    if "start_time" not in st.session_state:
        st.session_state.start_time = time.time()

def timer_mode(questions):
    st.subheader("Timer Mode")
    
    question_data = questions[st.session_state.question_index]
    st.write(question_data["question"])
    
    selected_option = st.radio("Choose an answer:", question_data["options"], key=f"timer_{st.session_state.question_index}")
    
    timer_duration = 10  # seconds
    elapsed_time = int(time.time() - st.session_state.start_time)
    remaining_time = max(0, timer_duration - elapsed_time)
    
    progress = remaining_time / timer_duration
    st.progress(progress)
    
    if remaining_time == 0 or st.button("Next Question"):
        st.session_state.timer_responses[st.session_state.question_index] = selected_option
        st.session_state.question_index += 1
        st.session_state.start_time = time.time()
        if st.session_state.question_index >= len(questions):
            st.session_state.mode = "relaxed"
            st.session_state.question_index = 0
        st.experimental_rerun()

def relaxed_mode(questions):
    st.subheader("Relaxed Mode")
    
    question_data = questions[st.session_state.question_index]
    st.write(question_data["question"])
    
    if st.session_state.question_index not in st.session_state.time_spent_relaxed:
        st.session_state.time_spent_relaxed[st.session_state.question_index] = 0
    
    start_relaxed = time.time()
    selected_option = st.radio("Choose an answer:", question_data["options"], key=f"relaxed_{st.session_state.question_index}")
    
    if st.button("Next Question"):
        st.session_state.relaxed_responses[st.session_state.question_index] = selected_option
        st.session_state.time_spent_relaxed[st.session_state.question_index] += time.time() - start_relaxed
        st.session_state.question_index += 1
        if st.session_state.question_index >= len(questions):
            st.session_state.mode = "completed"
        st.experimental_rerun()
    
    if st.session_state.question_index > 0 and st.button("Previous Question"):
        st.session_state.time_spent_relaxed[st.session_state.question_index] += time.time() - start_relaxed
        st.session_state.question_index -= 1
        st.experimental_rerun()

def main():
    st.title("Survey Application")
    questions = load_questions()
    init_session_state()
    
    if st.session_state.mode == "timer":
        timer_mode(questions)
    elif st.session_state.mode == "relaxed":
        relaxed_mode(questions)
    elif st.session_state.mode == "completed":
        st.success("Survey Completed!")
        st.json({
            "Timer Mode Responses": st.session_state.timer_responses,
            "Relaxed Mode Responses": st.session_state.relaxed_responses,
            "Time Spent (Relaxed Mode)": st.session_state.time_spent_relaxed
        })

if __name__ == "__main__":
    main()