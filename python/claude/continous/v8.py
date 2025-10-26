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
# Store the absolute start time of current question's timer
if 'current_timer_start_time' not in st.session_state:
    st.session_state.current_timer_start_time = time.time()
# Store selected option for current question in timer mode
if 'timer_current_selection' not in st.session_state:
    st.session_state.timer_current_selection = None
# For auto-update mechanism
if 'last_update' not in st.session_state:
    st.session_state.last_update = time.time()
# Track if timer should be reset
if 'reset_timer' not in st.session_state:
    st.session_state.reset_timer = True

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
            # Mark timer for reset
            st.session_state.reset_timer = True
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
    key = f"relaxed_radio_{idx}"
    if key in st.session_state:
        selected = st.session_state[key]
        if selected is not None:
            save_relaxed_answer(idx, selected)

def timer_selection_change():
    # Update the current selection without rerunning the page
    current_idx = st.session_state.current_question
    key = f"timer_radio_{current_idx}"
    if key in st.session_state:
        st.session_state.timer_current_selection = st.session_state[key]

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

def get_timer_progress():
    """Calculate the current timer progress value (0-1)"""
    if st.session_state.mode != "timer_mode":
        return 0
    
    current_idx = st.session_state.current_question
    time_limit = questions[current_idx]["time_limit"]
    elapsed_time = time.time() - st.session_state.current_timer_start_time
    remaining_time = max(0, time_limit - elapsed_time)
    
    # Return value between 0 and 1 representing remaining time
    return remaining_time / time_limit

def check_timer_expiration():
    """Check if the timer for current question has expired"""
    if st.session_state.mode != "timer_mode":
        return False
    
    current_idx = st.session_state.current_question
    time_limit = questions[current_idx]["time_limit"]
    elapsed_time = time.time() - st.session_state.current_timer_start_time
    
    # If time's up, save answer and move to next question
    if elapsed_time >= time_limit:
        # Save the answer (or "No answer" if none selected)
        st.session_state.timer_answers[current_idx] = (
            st.session_state.timer_current_selection if st.session_state.timer_current_selection else "No answer"
        )
        # Move to next question
        next_question()
        return True
    
    return False

def main():
    # Only reset timer when necessary (new question)
    if st.session_state.mode == "timer_mode" and st.session_state.reset_timer:
        st.session_state.current_timer_start_time = time.time()
        st.session_state.timer_current_selection = None
        st.session_state.reset_timer = False
    
    # Setup automatic refresh mechanism
    if st.session_state.mode == "timer_mode":
        # Timeout every 200ms to refresh the timer
        current_time = time.time()
        if current_time - st.session_state.last_update > 0.2:
            st.session_state.last_update = current_time
            # Check timer expiration before scheduling rerun
            if not check_timer_expiration():
                # Use a placeholder to force a rerun
                st.empty().markdown(f"<div id='timer-refresh'></div>", unsafe_allow_html=True)
                # Schedule a rerun after a short delay
                st.rerun()
    
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
        
        # Calculate remaining time
        elapsed_time = time.time() - st.session_state.current_timer_start_time
        remaining_time = max(0, time_limit - elapsed_time)
        
        # Calculate progress value (1.0 = full, 0.0 = empty)
        progress_value = get_timer_progress()
        
        # Timer display with container to group elements
        timer_container = st.container()
        with timer_container:
            col1, col2 = st.columns([6, 1])
            with col1:
                # Display progress bar with calculated value
                st.progress(progress_value)
            with col2:
                st.markdown(f"**{remaining_time:.1f}s**")
        
        # Radio button for answer selection
        option_index = None
        # Try to find the index for the current selection to maintain state
        if st.session_state.timer_current_selection in current_question["options"]:
            option_index = current_question["options"].index(st.session_state.timer_current_selection)
        
        selected_option = st.radio(
            "Select your answer:",
            options=current_question["options"],
            key=f"timer_radio_{current_idx}",
            index=option_index,
            on_change=timer_selection_change
        )
        
        # Submit button
        submitted = st.button("Submit", key=f"timer_submit_{current_idx}")
        
        # If submitted, save answer and go to next question
        if submitted:
            # Get the current selection from session state to avoid KeyError
            current_selection = st.session_state.timer_current_selection
            st.session_state.timer_answers[current_idx] = current_selection if current_selection else "No answer"
            next_question()
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
            index=default_idx if default_value and default_value in current_question["options"] else None,
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