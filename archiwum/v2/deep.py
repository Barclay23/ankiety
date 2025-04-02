import streamlit as st
import time
from datetime import datetime, timedelta
import pandas as pd

# Predefined survey questions
QUESTIONS = [
    "How satisfied are you with our product? (1-10)",
    "How likely are you to recommend us to a friend? (1-10)",
    "How would you rate our customer service? (1-10)",
    "How easy was it to use our product? (1-10)",
    "How would you rate the value for money? (1-10)"
]

def initialize_session_state():
    """Initialize all required session state variables"""
    if 'current_mode' not in st.session_state:
        st.session_state.current_mode = None
    if 'current_question' not in st.session_state:
        st.session_state.current_question = 0
    if 'answers' not in st.session_state:
        st.session_state.answers = {}
    if 'relaxed_start_times' not in st.session_state:
        st.session_state.relaxed_start_times = {}
    if 'time_spent' not in st.session_state:
        st.session_state.time_spent = {q: 0 for q in QUESTIONS}
    if 'timer_start' not in st.session_state:
        st.session_state.timer_start = None
    if 'completed_timer_mode' not in st.session_state:
        st.session_state.completed_timer_mode = False

def select_mode():
    """Let user select the survey mode"""
    st.title("Survey Mode Selection")
    st.write("Please select your preferred survey mode:")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Timer Mode ⏱️"):
            st.session_state.current_mode = "timer"
            st.session_state.current_question = 0
            st.session_state.timer_start = time.time()
            st.rerun()
    
    with col2:
        if st.button("Relaxed Mode 😌"):
            if not st.session_state.completed_timer_mode:
                st.warning("You must complete Timer Mode before entering Relaxed Mode.")
            else:
                st.session_state.current_mode = "relaxed"
                st.session_state.current_question = 0
                st.rerun()

def timer_mode():
    """Timer mode survey with countdown"""
    st.title("Survey - Timer Mode ⏱️")
    
    # Timer settings
    total_time = 30  # 30 seconds per question
    time_elapsed = time.time() - st.session_state.timer_start
    time_remaining = max(0, total_time - time_elapsed)
    
    # Progress bar timer
    progress = time_remaining / total_time
    st.progress(progress)
    
    # Time remaining display
    mins, secs = divmod(int(time_remaining), 60)
    st.subheader(f"Time remaining: {mins:02d}:{secs:02d}")
    
    # Display current question
    question = QUESTIONS[st.session_state.current_question]
    st.subheader(f"Question {st.session_state.current_question + 1}/{len(QUESTIONS)}")
    st.write(question)
    
    # Answer input
    answer = st.number_input("Your answer (1-10)", min_value=1, max_value=10, key=f"timer_q{st.session_state.current_question}")
    
    # Navigation buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Previous Question") and st.session_state.current_question > 0:
            st.session_state.current_question -= 1
            st.session_state.timer_start = time.time()  # Reset timer for new question
            st.rerun()
    
    with col2:
        if st.button("Next Question") or time_remaining <= 0:
            # Save answer
            st.session_state.answers[question] = answer
            
            if time_remaining <= 0:
                st.warning("Time's up! Moving to next question.")
            
            # Move to next question or finish
            if st.session_state.current_question < len(QUESTIONS) - 1:
                st.session_state.current_question += 1
                st.session_state.timer_start = time.time()  # Reset timer for new question
                st.rerun()
            else:
                st.session_state.completed_timer_mode = True
                st.success("Timer Mode completed! Now please proceed to Relaxed Mode.")
                time.sleep(2)
                st.session_state.current_mode = None
                st.rerun()

def relaxed_mode():
    """Relaxed mode survey with no time limit"""
    st.title("Survey - Relaxed Mode 😌")
    
    # Display current question
    question = QUESTIONS[st.session_state.current_question]
    st.subheader(f"Question {st.session_state.current_question + 1}/{len(QUESTIONS)}")
    st.write(question)
    
    # Track time spent on this question
    if question not in st.session_state.relaxed_start_times:
        st.session_state.relaxed_start_times[question] = time.time()
    
    # Answer input (pre-populate if answered in timer mode)
    default_value = st.session_state.answers.get(question, None)
    answer = st.number_input(
        "Your answer (1-10)", 
        min_value=1, 
        max_value=10, 
        value=default_value if default_value else 1,
        key=f"relaxed_q{st.session_state.current_question}"
    )
    
    # Navigation buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Previous Question") and st.session_state.current_question > 0:
            # Record time spent on current question before moving
            current_time = time.time()
            start_time = st.session_state.relaxed_start_times.pop(question, current_time)
            st.session_state.time_spent[question] += current_time - start_time
            
            st.session_state.current_question -= 1
            st.rerun()
    
    with col2:
        if st.button("Next Question") and st.session_state.current_question < len(QUESTIONS) - 1:
            # Record time spent on current question before moving
            current_time = time.time()
            start_time = st.session_state.relaxed_start_times.pop(question, current_time)
            st.session_state.time_spent[question] += current_time - start_time
            
            st.session_state.current_question += 1
            st.rerun()
    
    with col3:
        if st.button("Finish Survey"):
            # Record time spent on current question before finishing
            current_time = time.time()
            start_time = st.session_state.relaxed_start_times.pop(question, current_time)
            st.session_state.time_spent[question] += current_time - start_time
            
            # Save final answer
            st.session_state.answers[question] = answer
            
            # Show results
            show_results()
            return
    
    # Auto-save answer (in case user doesn't click next/finish)
    st.session_state.answers[question] = answer

def show_results():
    """Display survey results"""
    st.title("Survey Results")
    st.write("Thank you for completing the survey! Here are your answers:")
    
    # Prepare data for display
    results = []
    for question in QUESTIONS:
        results.append({
            "Question": question,
            "Your Answer": st.session_state.answers.get(question, "Not answered"),
            "Time Spent (Relaxed Mode)": f"{st.session_state.time_spent[question]:.1f} sec" 
            if st.session_state.time_spent[question] > 0 else "N/A"
        })
    
    # Display as table
    st.table(pd.DataFrame(results))
    
    # Option to start over
    if st.button("Start New Survey"):
        # Reset all state except completed_timer_mode to prevent going back to timer mode
        st.session_state.current_mode = None
        st.session_state.current_question = 0
        st.session_state.answers = {}
        st.session_state.relaxed_start_times = {}
        st.session_state.time_spent = {q: 0 for q in QUESTIONS}
        st.session_state.timer_start = None
        st.rerun()

def main():
    """Main application logic"""
    initialize_session_state()
    
    if st.session_state.current_mode == "timer":
        timer_mode()
    elif st.session_state.current_mode == "relaxed":
        relaxed_mode()
    else:
        select_mode()

if __name__ == "__main__":
    main()