import streamlit as st
import time
import datetime
import pandas as pd
import json
import threading

# Set page configuration
st.set_page_config(
    page_title="Survey Application",
    page_icon="📝",
    layout="wide"
)

# Enable auto-refresh for timer
if 'auto_refresh' not in st.session_state:
    st.session_state.auto_refresh = True

# Sample questions - replace with your own
QUESTIONS = [
    {
        "question": "What is the capital of France?",
        "options": ["London", "Paris", "Berlin", "Madrid"],
        "correct": "Paris"
    },
    {
        "question": "Which programming language is this application written in?",
        "options": ["JavaScript", "Python", "Java", "C++"],
        "correct": "Python"
    },
    {
        "question": "What is 7 x 8?",
        "options": ["54", "56", "58", "64"],
        "correct": "56"
    },
    {
        "question": "Which planet is known as the Red Planet?",
        "options": ["Venus", "Mars", "Jupiter", "Saturn"],
        "correct": "Mars"
    },
    {
        "question": "Who wrote 'Romeo and Juliet'?",
        "options": ["Charles Dickens", "William Shakespeare", "Jane Austen", "Mark Twain"],
        "correct": "William Shakespeare"
    }
]

# Time limit per question in seconds
TIME_LIMIT_PER_QUESTION = 10  # Default: 10 seconds

def initialize_session_state():
    """Initialize all session state variables if they don't exist"""
    if 'mode' not in st.session_state:
        st.session_state.mode = "timer"  # Start with timer mode
    
    if 'current_question' not in st.session_state:
        st.session_state.current_question = 0
    
    if 'timer_answers' not in st.session_state:
        st.session_state.timer_answers = [None] * len(QUESTIONS)
    
    if 'relaxed_answers' not in st.session_state:
        st.session_state.relaxed_answers = [None] * len(QUESTIONS)
    
    if 'timer_completed' not in st.session_state:
        st.session_state.timer_completed = False
    
    if 'time_started' not in st.session_state:
        st.session_state.time_started = time.time()
    
    if 'question_durations_relaxed' not in st.session_state:
        st.session_state.question_durations_relaxed = [0] * len(QUESTIONS)
    
    if 'relaxed_start_time' not in st.session_state:
        st.session_state.relaxed_start_time = None
        
    if 'last_refresh_time' not in st.session_state:
        st.session_state.last_refresh_time = time.time()

def go_to_next_question():
    """Move to the next question in the sequence"""
    if st.session_state.current_question < len(QUESTIONS) - 1:
        st.session_state.current_question += 1
        st.session_state.time_started = time.time()
    else:
        st.session_state.timer_completed = True
        st.session_state.mode = "relaxed"
        st.session_state.current_question = 0
        st.session_state.relaxed_start_time = time.time()

def record_timer_answer(answer, question_idx):
    """Record answer given in timer mode"""
    st.session_state.timer_answers[question_idx] = answer

def record_relaxed_answer(answer, question_idx):
    """Record answer given in relaxed mode"""
    # Calculate and save the time spent on this question
    current_time = time.time()
    if st.session_state.relaxed_start_time is not None:
        duration = current_time - st.session_state.relaxed_start_time
        st.session_state.question_durations_relaxed[question_idx] = duration
    
    # Save the answer
    st.session_state.relaxed_answers[question_idx] = answer
    
    # Reset timer for the next question
    st.session_state.relaxed_start_time = current_time

def display_timer_bar(time_left, total_time):
    """Display a shrinking timer bar"""
    progress = time_left / total_time
    # Use a color that changes from green to red as time runs out
    color = f"rgb({int(255 * (1 - progress))}, {int(255 * progress)}, 0)"
    
    st.markdown(
        f"""
        <div style="
            width: 100%;
            height: 20px;
            background-color: #f0f0f0;
            border-radius: 5px;
            margin-bottom: 20px;
        ">
            <div style="
                width: {progress * 100}%;
                height: 20px;
                background-color: {color};
                border-radius: 5px;
                transition: width 0.1s linear;
            "></div>
        </div>
        <div style="text-align: center; font-weight: bold; margin-bottom: 20px;">
            Time remaining: {int(time_left)} seconds
        </div>
        """,
        unsafe_allow_html=True
    )

def save_results():
    """Save the survey results to a downloadable format"""
    results = {
        "timer_mode_answers": st.session_state.timer_answers,
        "relaxed_mode_answers": st.session_state.relaxed_answers,
        "relaxed_mode_durations_seconds": st.session_state.question_durations_relaxed
    }
    
    # Format results for display
    df = pd.DataFrame({
        "Question": [q["question"] for q in QUESTIONS],
        "Timer Mode Answer": st.session_state.timer_answers,
        "Relaxed Mode Answer": st.session_state.relaxed_answers,
        "Time Spent (Relaxed Mode)": [f"{duration:.2f} seconds" for duration in st.session_state.question_durations_relaxed]
    })
    
    # Display results
    st.subheader("Survey Results")
    st.dataframe(df)
    
    # Download options
    results_json = json.dumps(results, indent=4)
    st.download_button(
        label="Download Results (JSON)",
        data=results_json,
        file_name="survey_results.json",
        mime="application/json"
    )
    
    # CSV download
    csv = df.to_csv(index=False)
    st.download_button(
        label="Download Results (CSV)",
        data=csv,
        file_name="survey_results.csv",
        mime="text/csv"
    )

def timer_mode():
    """Display the timer mode interface"""
    st.header("Timer Mode")
    st.subheader(f"Question {st.session_state.current_question + 1} of {len(QUESTIONS)}")
    
    # Calculate time elapsed and remaining
    current_time = time.time()
    time_elapsed = current_time - st.session_state.time_started
    time_left = max(0, TIME_LIMIT_PER_QUESTION - time_elapsed)
    
    # Display timer bar
    display_timer_bar(time_left, TIME_LIMIT_PER_QUESTION)
    
    # Display the current question
    question_data = QUESTIONS[st.session_state.current_question]
    st.markdown(f"### {question_data['question']}")
    
    # Display the options
    col1, col2 = st.columns([3, 1])
    with col1:
        answer = st.radio(
            "Select your answer:",
            question_data["options"],
            key=f"timer_q{st.session_state.current_question}",
            index=None,
            horizontal=True
        )
        
        if answer:
            record_timer_answer(answer, st.session_state.current_question)
    
    # Check if time is up
    if time_left <= 0:
        go_to_next_question()
        st.rerun()
    elif st.session_state.auto_refresh:
        # Only refresh if it's been at least 0.1 seconds since the last refresh
        if time.time() - st.session_state.last_refresh_time >= 0.1:
            st.session_state.last_refresh_time = time.time()
            time.sleep(0.01)  # Short delay to avoid excessive CPU usage
            st.rerun()

def relaxed_mode():
    """Display the relaxed mode interface"""
    st.header("Relaxed Mode")
    st.info("Take your time to answer each question. You can navigate between questions freely.")
    
    # Initialize relaxed start time if this is the first time entering relaxed mode
    if st.session_state.relaxed_start_time is None:
        st.session_state.relaxed_start_time = time.time()
    
    # Question navigation
    col1, col2, col3 = st.columns([1, 3, 1])
    with col1:
        if st.button("Previous Question", disabled=st.session_state.current_question == 0):
            # Save time spent on current question before moving
            current_time = time.time()
            duration = current_time - st.session_state.relaxed_start_time
            st.session_state.question_durations_relaxed[st.session_state.current_question] = duration
            
            st.session_state.current_question -= 1
            st.session_state.relaxed_start_time = time.time()
            st.rerun()
    
    with col3:
        next_button_text = "Next Question" if st.session_state.current_question < len(QUESTIONS) - 1 else "Finish Survey"
        if st.button(next_button_text):
            # Save time spent on current question before moving
            current_time = time.time()
            duration = current_time - st.session_state.relaxed_start_time
            st.session_state.question_durations_relaxed[st.session_state.current_question] = duration
            
            if st.session_state.current_question < len(QUESTIONS) - 1:
                st.session_state.current_question += 1
                st.session_state.relaxed_start_time = time.time()
                st.rerun()
            else:
                # Survey is complete, show summary
                st.session_state.mode = "complete"
                st.rerun()
    
    with col2:
        st.progress((st.session_state.current_question + 1) / len(QUESTIONS))
        st.caption(f"Question {st.session_state.current_question + 1} of {len(QUESTIONS)}")
    
    # Display the current question
    question_data = QUESTIONS[st.session_state.current_question]
    st.markdown(f"### {question_data['question']}")
    
    # Show the timer answer for reference
    timer_answer = st.session_state.timer_answers[st.session_state.current_question]
    if timer_answer:
        st.info(f"Your answer in Timer Mode: {timer_answer}")
    else:
        st.warning("You didn't answer this question in Timer Mode.")
    
    # Display the options
    answer = st.radio(
        "Select your answer:",
        question_data["options"],
        key=f"relaxed_q{st.session_state.current_question}",
        index=question_data["options"].index(st.session_state.relaxed_answers[st.session_state.current_question]) if st.session_state.relaxed_answers[st.session_state.current_question] else None,
        horizontal=True
    )
    
    if answer:
        record_relaxed_answer(answer, st.session_state.current_question)

def complete_screen():
    """Display the survey completion screen"""
    st.header("Survey Completed!")
    st.success("Thank you for completing both parts of the survey.")
    
    save_results()
    
    # Option to restart
    if st.button("Start New Survey"):
        # Reset all session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        initialize_session_state()
        st.rerun()

def main():
    """Main function to run the survey application"""
    # Initialize session state
    initialize_session_state()
    
    # Display app title
    st.title("Two-Mode Survey Application")
    
    # Add hidden element with auto-refresh for timer mode
    if st.session_state.mode == "timer" and st.session_state.auto_refresh:
        st.markdown(
            """
            <iframe src="data:text/html;charset=utf-8,%3Chtml%3E%3Cbody%3E%3Cscript%3Efunction refresh() %7B parent.window.location.reload(); setTimeout(refresh%2C 100); %7D setTimeout(refresh%2C 100)%3B%3C/script%3E%3C/body%3E%3C/html%3E" 
            width="0" height="0" style="display:none;">
            </iframe>
            """,
            unsafe_allow_html=True
        )
    
    # Display instructions based on current mode
    if st.session_state.mode == "timer":
        timer_mode()
    elif st.session_state.mode == "relaxed":
        relaxed_mode()
    elif st.session_state.mode == "complete":
        complete_screen()

if __name__ == "__main__":
    main()