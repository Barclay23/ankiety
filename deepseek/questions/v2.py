import streamlit as st
import time
import pandas as pd

# App configuration must be first
st.set_page_config(page_title="Survey App", layout="wide")

# Set Streamlit version (after page config)
st.write(f"Streamlit version: {st.__version__}")

# Survey questions
QUESTIONS = [
    {
        "question": "How often do you use Python for work?",
        "options": ["Daily", "Weekly", "Monthly", "Rarely", "Never"]
    },
    {
        "question": "How comfortable are you with Streamlit?",
        "options": ["Very comfortable", "Comfortable", "Neutral", "Uncomfortable", "Very uncomfortable"]
    },
    {
        "question": "How likely are you to recommend this survey to others?",
        "options": ["Very likely", "Likely", "Neutral", "Unlikely", "Very unlikely"]
    }
]

def initialize_session_state():
    """Initialize all session state variables"""
    if 'mode' not in st.session_state:
        st.session_state.mode = None
    if 'current_question' not in st.session_state:
        st.session_state.current_question = 0
    if 'timer_start' not in st.session_state:
        st.session_state.timer_start = None
    if 'timer_duration' not in st.session_state:
        st.session_state.timer_duration = 15  # seconds per question in timer mode
    if 'timer_remaining' not in st.session_state:
        st.session_state.timer_remaining = st.session_state.timer_duration
    if 'answers_timer' not in st.session_state:
        st.session_state.answers_timer = [None] * len(QUESTIONS)
    if 'answers_relaxed' not in st.session_state:
        st.session_state.answers_relaxed = [None] * len(QUESTIONS)
    if 'relaxed_start_times' not in st.session_state:
        st.session_state.relaxed_start_times = [None] * len(QUESTIONS)
    if 'time_spent_relaxed' not in st.session_state:
        st.session_state.time_spent_relaxed = [0] * len(QUESTIONS)
    if 'survey_complete' not in st.session_state:
        st.session_state.survey_complete = False

# Timer mode functions
def start_timer_mode():
    st.session_state.mode = "timer"
    st.session_state.current_question = 0
    st.session_state.timer_start = time.time()
    st.session_state.timer_remaining = st.session_state.timer_duration
    st.session_state.answers_timer = [None] * len(QUESTIONS)

def next_question():
    if st.session_state.current_question < len(QUESTIONS) - 1:
        st.session_state.current_question += 1
        st.session_state.timer_start = time.time()
        st.session_state.timer_remaining = st.session_state.timer_duration
    else:
        # Timer mode completed, switch to relaxed mode
        st.session_state.mode = "relaxed"
        st.session_state.current_question = 0
        st.session_state.relaxed_start_times[0] = time.time()

def update_timer():
    if st.session_state.mode == "timer" and st.session_state.timer_start:
        elapsed = time.time() - st.session_state.timer_start
        st.session_state.timer_remaining = max(0, st.session_state.timer_duration - elapsed)
        
        if st.session_state.timer_remaining <= 0:
            next_question()

# Relaxed mode functions
def prev_question_relaxed():
    if st.session_state.current_question > 0:
        # Record time spent on current question
        if st.session_state.relaxed_start_times[st.session_state.current_question]:
            time_spent = time.time() - st.session_state.relaxed_start_times[st.session_state.current_question]
            st.session_state.time_spent_relaxed[st.session_state.current_question] += time_spent
        
        st.session_state.current_question -= 1
        st.session_state.relaxed_start_times[st.session_state.current_question] = time.time()

def next_question_relaxed():
    if st.session_state.current_question < len(QUESTIONS) - 1:
        # Record time spent on current question
        if st.session_state.relaxed_start_times[st.session_state.current_question]:
            time_spent = time.time() - st.session_state.relaxed_start_times[st.session_state.current_question]
            st.session_state.time_spent_relaxed[st.session_state.current_question] += time_spent
        
        st.session_state.current_question += 1
        st.session_state.relaxed_start_times[st.session_state.current_question] = time.time()
    else:
        complete_survey()

def complete_survey():
    # Record time spent on last question
    if st.session_state.relaxed_start_times[st.session_state.current_question]:
        time_spent = time.time() - st.session_state.relaxed_start_times[st.session_state.current_question]
        st.session_state.time_spent_relaxed[st.session_state.current_question] += time_spent
    
    st.session_state.survey_complete = True

def show_results():
    """Display survey results"""
    st.success("Survey completed! Thank you for your participation.")
    
    # Display results
    st.subheader("Your Answers")
    results = []
    for i, q in enumerate(QUESTIONS):
        results.append({
            "Question": q["question"],
            "Timer Mode Answer": q["options"][st.session_state.answers_timer[i]] if st.session_state.answers_timer[i] is not None else "Not answered",
            "Relaxed Mode Answer": q["options"][st.session_state.answers_relaxed[i]] if st.session_state.answers_relaxed[i] is not None else "Not answered",
            "Time Spent in Relaxed Mode (seconds)": round(st.session_state.time_spent_relaxed[i], 2)
        })
    
    st.dataframe(pd.DataFrame(results))
    
    if st.button("Start New Survey"):
        # Reset session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

def show_mode_selection():
    """Show the initial mode selection screen"""
    st.subheader("Select Survey Mode")
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Timer Mode**")
        st.write("- Questions with time limit")
        st.write("- Progress automatically")
        st.write("- Stressful environment")
        if st.button("Start Timer Mode"):
            start_timer_mode()
            st.rerun()
    
    with col2:
        st.write("**Relaxed Mode**")
        st.write("- No time limit")
        st.write("- Go back and forth")
        st.write("- Calm environment")
        st.button("Start Relaxed Mode", disabled=True, 
                  help="You must complete Timer Mode first")

def show_timer_mode():
    """Display the timer mode interface"""
    st.subheader("Timer Mode")
    
    # Timer progress bar
    progress = st.session_state.timer_remaining / st.session_state.timer_duration
    st.progress(progress)
    
    # Display time remaining
    st.write(f"Time remaining: {int(st.session_state.timer_remaining)} seconds")
    
    # Display current question
    q = QUESTIONS[st.session_state.current_question]
    st.write(f"Question {st.session_state.current_question + 1}/{len(QUESTIONS)}")
    st.subheader(q["question"])
    
    # Answer options
    answer = st.radio(
        "Select your answer:",
        q["options"],
        index=st.session_state.answers_timer[st.session_state.current_question] if st.session_state.answers_timer[st.session_state.current_question] is not None else None,
        key=f"timer_q{st.session_state.current_question}"
    )
    
    # Store answer
    if answer:
        st.session_state.answers_timer[st.session_state.current_question] = q["options"].index(answer)
    
    # Next button (optional since timer will auto-progress)
    st.button("Next Question", on_click=next_question)
    
    # Update timer continuously
    update_timer()
    time.sleep(0.1)
    st.rerun()

def show_relaxed_mode():
    """Display the relaxed mode interface"""
    st.subheader("Relaxed Mode")
    
    # Display current question
    q = QUESTIONS[st.session_state.current_question]
    st.write(f"Question {st.session_state.current_question + 1}/{len(QUESTIONS)}")
    st.subheader(q["question"])
    
    # Answer options
    answer = st.radio(
        "Select your answer:",
        q["options"],
        index=st.session_state.answers_relaxed[st.session_state.current_question] if st.session_state.answers_relaxed[st.session_state.current_question] is not None else None,
        key=f"relaxed_q{st.session_state.current_question}"
    )
    
    # Store answer
    if answer:
        st.session_state.answers_relaxed[st.session_state.current_question] = q["options"].index(answer)
    
    # Navigation buttons
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.session_state.current_question > 0:
            st.button("← Previous Question", on_click=prev_question_relaxed)
    with col2:
        if st.session_state.current_question < len(QUESTIONS) - 1:
            st.button("Next Question →", on_click=next_question_relaxed)
        else:
            st.button("Complete Survey", on_click=complete_survey)
    
    # Display time spent on current question
    if st.session_state.relaxed_start_times[st.session_state.current_question]:
        current_time_spent = time.time() - st.session_state.relaxed_start_times[st.session_state.current_question]
        total_time_spent = st.session_state.time_spent_relaxed[st.session_state.current_question] + current_time_spent
        st.write(f"Time spent on this question: {round(total_time_spent, 1)} seconds")

# Main app
def main():
    st.title("Survey Application")
    initialize_session_state()
    
    if st.session_state.survey_complete:
        show_results()
        return
    
    if st.session_state.mode is None:
        show_mode_selection()
    elif st.session_state.mode == "timer":
        show_timer_mode()
    elif st.session_state.mode == "relaxed":
        show_relaxed_mode()

if __name__ == "__main__":
    main()