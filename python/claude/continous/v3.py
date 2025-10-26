import streamlit as st
import time
import pandas as pd
from datetime import datetime

# Set page config
st.set_page_config(page_title="Dual-Mode Survey Application", layout="wide")

# Initialize session state variables if they don't exist
if 'mode' not in st.session_state:
    st.session_state.mode = "timer_mode"  # Start with timer mode
if 'current_question' not in st.session_state:
    st.session_state.current_question = 0
if 'timer_answers' not in st.session_state:
    st.session_state.timer_answers = {}
if 'relaxed_answers' not in st.session_state:
    st.session_state.relaxed_answers = {}
if 'timer_mode_completed' not in st.session_state:
    st.session_state.timer_mode_completed = False
if 'question_start_time' not in st.session_state:
    st.session_state.question_start_time = None
if 'relaxed_time_spent' not in st.session_state:
    st.session_state.relaxed_time_spent = {}
# Track timer start time for each question
if 'question_timer_starts' not in st.session_state:
    st.session_state.question_timer_starts = {}
# Keep track of which questions have timers initialized
if 'timer_initialized' not in st.session_state:
    st.session_state.timer_initialized = False
# Store the last auto refresh time
if 'last_refresh_time' not in st.session_state:
    st.session_state.last_refresh_time = time.time()

# Sample questions with multiple choice options
questions = [
    {
        "question": "What is the capital of France?",
        "options": ["Berlin", "Madrid", "Paris", "Rome"],
        "time_limit": 10  # seconds
    },
    {
        "question": "Which planet is known as the Red Planet?",
        "options": ["Earth", "Mars", "Jupiter", "Venus"],
        "time_limit": 8  # seconds
    },
    {
        "question": "What is 2 + 2?",
        "options": ["3", "4", "5", "6"],
        "time_limit": 5  # seconds
    },
    {
        "question": "Who wrote 'Romeo and Juliet'?",
        "options": ["Charles Dickens", "William Shakespeare", "Jane Austen", "Mark Twain"],
        "time_limit": 12  # seconds
    },
]

def switch_to_relaxed_mode():
    st.session_state.mode = "relaxed_mode"
    st.session_state.current_question = 0
    st.session_state.timer_mode_completed = True
    st.session_state.question_start_time = datetime.now()

def next_question():
    if st.session_state.current_question < len(questions) - 1:
        st.session_state.current_question += 1
        if st.session_state.mode == "relaxed_mode":
            st.session_state.question_start_time = datetime.now()
        elif st.session_state.mode == "timer_mode":
            # Initialize timer for the new question
            current_idx = st.session_state.current_question
            if current_idx not in st.session_state.question_timer_starts:
                st.session_state.question_timer_starts[current_idx] = time.time()
            st.session_state.timer_initialized = True
    else:
        if st.session_state.mode == "timer_mode":
            switch_to_relaxed_mode()
        else:
            st.session_state.mode = "completed"

def previous_question():
    if st.session_state.current_question > 0:
        st.session_state.current_question -= 1
        if st.session_state.mode == "relaxed_mode":
            st.session_state.question_start_time = datetime.now()

def save_relaxed_answer(idx, selected_option):
    # Save the current answer and update time spent
    st.session_state.relaxed_answers[idx] = selected_option
    if st.session_state.question_start_time is not None:
        time_spent = (datetime.now() - st.session_state.question_start_time).total_seconds()
        # If there's already time recorded for this question, add to it
        current_time = st.session_state.relaxed_time_spent.get(idx, 0)
        st.session_state.relaxed_time_spent[idx] = current_time + time_spent
        st.session_state.question_start_time = datetime.now()

def on_answer_change(idx):
    # This function is called when the radio button value changes
    selected = st.session_state[f"relaxed_radio_{idx}"]
    if selected is not None:
        save_relaxed_answer(idx, selected)

def display_results():
    st.title("Survey Results")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Timer Mode Answers")
        timer_results = {}
        for i, q in enumerate(questions):
            timer_results[f"Question {i+1}"] = st.session_state.timer_answers.get(i, "No answer")
        st.table(pd.DataFrame(timer_results.items(), columns=["Question", "Your Answer"]))
    
    with col2:
        st.subheader("Relaxed Mode Answers")
        relaxed_results = {}
        time_spent = {}
        for i, q in enumerate(questions):
            relaxed_results[f"Question {i+1}"] = st.session_state.relaxed_answers.get(i, "No answer")
            time_spent[f"Question {i+1}"] = f"{st.session_state.relaxed_time_spent.get(i, 0):.2f} seconds"
        
        results_df = pd.DataFrame({
            "Question": list(relaxed_results.keys()),
            "Your Answer": list(relaxed_results.values()),
            "Time Spent": list(time_spent.values())
        })
        st.table(results_df)

def initialize_question_timer(current_idx):
    """Initialize timer for current question if not already set"""
    if current_idx not in st.session_state.question_timer_starts:
        st.session_state.question_timer_starts[current_idx] = time.time()
        st.session_state.timer_initialized = True

def check_timer_progress(current_idx, time_limit, selected_option):
    """Check timer progress and process accordingly"""
    # Initialize timer if needed
    if not st.session_state.timer_initialized or current_idx not in st.session_state.question_timer_starts:
        initialize_question_timer(current_idx)
    
    # Calculate time remaining
    start_time = st.session_state.question_timer_starts[current_idx]
    current_time = time.time()
    elapsed_time = current_time - start_time
    remaining_time = time_limit - elapsed_time
    remaining_ratio = max(0, remaining_time / time_limit)
    
    # Check if timer has expired
    if remaining_time <= 0:
        # Save answer (or "No answer" if none selected)
        st.session_state.timer_answers[current_idx] = selected_option if selected_option else "No answer"
        # Move to next question
        next_question()
        return True, 0  # Timer expired, needs rerun
    
    # Schedule next auto-refresh if needed
    current_time = time.time()
    if current_time - st.session_state.last_refresh_time > 0.2:  # Refresh every 200ms
        st.session_state.last_refresh_time = current_time
        return True, remaining_ratio  # Time for a refresh
    
    return False, remaining_ratio  # No action needed

def main():
    st.title("Dual-Mode Survey Application")
    
    # Display header based on current mode
    if st.session_state.mode == "timer_mode":
        st.header("Timer Mode - Answer Quickly!")
        st.warning("⏰ Answer the questions before time runs out! You cannot go back to previous questions.")
    elif st.session_state.mode == "relaxed_mode":
        st.header("Relaxed Mode - Take Your Time")
        st.info("Take your time to answer each question. You can navigate back to previous questions.")
    elif st.session_state.mode == "completed":
        display_results()
        return
    
    current_idx = st.session_state.current_question
    current_question = questions[current_idx]
    
    # Display question number and progress
    st.subheader(f"Question {current_idx + 1}/{len(questions)}")
    
    # Display the question
    st.write(current_question["question"])
    
    # Store current time when entering a new question in relaxed mode
    if st.session_state.mode == "relaxed_mode" and st.session_state.question_start_time is None:
        st.session_state.question_start_time = datetime.now()
    
    # Handle timer mode
    if st.session_state.mode == "timer_mode":
        # Get time limit for current question
        time_limit = current_question["time_limit"]
        
        # Create timer placeholder
        timer_placeholder = st.empty()
        
        # Create radio button placeholder
        radio_placeholder = st.empty()
        
        # Create submit button placeholder
        submit_btn_placeholder = st.empty()
        
        # Radio button for answer selection
        selected_option = radio_placeholder.radio(
            "Select your answer:",
            options=current_question["options"],
            key=f"timer_radio_{current_idx}",
            index=None
        )
        
        # Submit button
        submitted = submit_btn_placeholder.button("Submit", key=f"timer_submit_{current_idx}")
        
        # If submitted, save answer and go to next question
        if submitted:
            st.session_state.timer_answers[current_idx] = selected_option if selected_option else "No answer"
            next_question()
            st.rerun()
        
        # Check timer and update progress bar
        needs_refresh, remaining_ratio = check_timer_progress(current_idx, time_limit, selected_option)
        timer_placeholder.progress(remaining_ratio)
        
        # Auto-refresh the page if needed (timer expired or refresh interval reached)
        if needs_refresh:
            time.sleep(0.1)  # Small delay to allow UI to update
            st.rerun()
    
    # Handle relaxed mode
    elif st.session_state.mode == "relaxed_mode":
        # Initialize with timer mode answer if available
        default_idx = None
        default_value = st.session_state.relaxed_answers.get(current_idx, None)
        
        if default_value is None and current_idx in st.session_state.timer_answers:
            timer_answer = st.session_state.timer_answers[current_idx]
            if timer_answer != "No answer" and timer_answer in current_question["options"]:
                default_idx = current_question["options"].index(timer_answer)
                default_value = timer_answer
        
        # Radio button for answer selection with callback
        selected_option = st.radio(
            "Select your answer:",
            options=current_question["options"],
            key=f"relaxed_radio_{current_idx}",
            index=default_idx if default_value in current_question["options"] else None,
            on_change=lambda: on_answer_change(current_idx)
        )
        
        # Navigation buttons
        col1, col2 = st.columns(2)
        
        with col1:
            if st.session_state.current_question > 0:
                if st.button("Previous Question"):
                    # The current answer is already saved via the on_change callback
                    previous_question()
                    st.rerun()
        
        with col2:
            if st.button("Next Question" if current_idx < len(questions) - 1 else "Finish Survey"):
                # The current answer is already saved via the on_change callback
                next_question()
                st.rerun()

if __name__ == "__main__":
    main()