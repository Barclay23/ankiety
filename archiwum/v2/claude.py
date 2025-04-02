import streamlit as st
import time
import pandas as pd
from datetime import datetime

def main():
    # Initialize session state for storing responses and timers
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
        st.session_state.current_mode = "timer"  # Start in timer mode
        st.session_state.current_question = 0
        st.session_state.timer_active = False
        st.session_state.time_started = 0
        st.session_state.time_per_question = 30  # Default time limit in seconds
        st.session_state.questions = [
            "What is your favorite programming language?",
            "How many years of experience do you have in software development?",
            "What is your preferred development environment?",
            "Which frontend framework do you prefer?",
            "What database technology do you typically use?"
        ]
        st.session_state.timer_answers = [""] * len(st.session_state.questions)
        st.session_state.relaxed_answers = [""] * len(st.session_state.questions)
        st.session_state.relaxed_times = [0] * len(st.session_state.questions)
        st.session_state.relaxed_start_times = [0] * len(st.session_state.questions)
        st.session_state.timer_completed = False
        st.session_state.relaxed_completed = False
    
    # App title
    st.title("Developer Survey Application")
    
    # Display current mode
    if st.session_state.current_mode == "timer":
        st.header("⏱️ TIMER MODE")
        display_timer_mode()
    elif st.session_state.current_mode == "relaxed":
        st.header("🧘 RELAXED MODE")
        display_relaxed_mode()
    elif st.session_state.current_mode == "results":
        display_results()

def display_timer_mode():
    if st.session_state.timer_completed:
        st.success("Timer mode completed! Moving to relaxed mode.")
        st.session_state.current_mode = "relaxed"
        st.session_state.current_question = 0
        st.rerun()
    
    # Calculate time remaining
    if st.session_state.timer_active:
        elapsed_time = time.time() - st.session_state.time_started
        remaining_time = max(0, st.session_state.time_per_question - elapsed_time)
        
        # Display the timer bar
        progress_value = remaining_time / st.session_state.time_per_question
        progress_color = "normal"
        if progress_value < 0.3:
            progress_color = "error"
        elif progress_value < 0.7:
            progress_color = "warning"
        
        st.progress(progress_value, text=f"Time remaining: {int(remaining_time)} seconds", color=progress_color)
        
        # Auto-move to next question when timer expires
        if remaining_time <= 0:
            # Record empty answer if time ran out
            move_to_next_question_timer()
            return
    else:
        if st.button("Start Timer Mode"):
            st.session_state.timer_active = True
            st.session_state.time_started = time.time()
            st.rerun()
            return
        st.warning("Click the button above to start the timed survey.")
        return
    
    # Display current question
    current_q = st.session_state.current_question
    st.subheader(f"Question {current_q + 1} of {len(st.session_state.questions)}")
    st.write(st.session_state.questions[current_q])
    
    # Input for answer
    answer = st.text_area("Your answer:", key=f"timer_q{current_q}", value=st.session_state.timer_answers[current_q])
    
    # Submit button to move to next question
    if st.button("Submit Answer"):
        st.session_state.timer_answers[current_q] = answer
        move_to_next_question_timer()

def move_to_next_question_timer():
    current_q = st.session_state.current_question
    next_q = current_q + 1
    
    if next_q < len(st.session_state.questions):
        st.session_state.current_question = next_q
        st.session_state.time_started = time.time()
    else:
        st.session_state.timer_active = False
        st.session_state.timer_completed = True
    
    st.rerun()

def display_relaxed_mode():
    if not st.session_state.timer_completed:
        st.error("You must complete Timer Mode first.")
        st.session_state.current_mode = "timer"
        st.rerun()
        return
    
    if st.session_state.relaxed_completed:
        st.success("Survey completed! View your results below.")
        st.session_state.current_mode = "results"
        st.rerun()
        return
    
    current_q = st.session_state.current_question
    
    # Initialize timing for this question if newly arrived
    if st.session_state.relaxed_start_times[current_q] == 0:
        st.session_state.relaxed_start_times[current_q] = time.time()
    
    # Display question navigation
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if current_q > 0:
            if st.button("Previous Question"):
                # Record time spent on current question before moving
                if st.session_state.relaxed_start_times[current_q] > 0:
                    time_spent = time.time() - st.session_state.relaxed_start_times[current_q]
                    st.session_state.relaxed_times[current_q] += time_spent
                
                st.session_state.current_question = current_q - 1
                # Reset start time for the previous question
                st.session_state.relaxed_start_times[current_q - 1] = time.time()
                st.rerun()
    
    with col3:
        if current_q < len(st.session_state.questions) - 1:
            next_button_label = "Next Question"
        else:
            next_button_label = "Finish Survey"
        
        if st.button(next_button_label):
            # Save the current answer
            st.session_state.relaxed_answers[current_q] = st.session_state.relaxed_input
            
            # Record time spent on this question
            if st.session_state.relaxed_start_times[current_q] > 0:
                time_spent = time.time() - st.session_state.relaxed_start_times[current_q]
                st.session_state.relaxed_times[current_q] += time_spent
            
            if current_q < len(st.session_state.questions) - 1:
                st.session_state.current_question = current_q + 1
                st.rerun()
            else:
                st.session_state.relaxed_completed = True
                st.rerun()
    
    # Display current question
    st.subheader(f"Question {current_q + 1} of {len(st.session_state.questions)}")
    st.write(st.session_state.questions[current_q])
    
    # Show what was answered in timer mode
    st.info(f"Your answer in timer mode: {st.session_state.timer_answers[current_q]}")
    
    # Input for relaxed mode answer
    if 'relaxed_input' not in st.session_state:
        st.session_state.relaxed_input = st.session_state.relaxed_answers[current_q]
    
    st.session_state.relaxed_input = st.text_area(
        "Take your time and provide a more detailed answer if you wish:",
        value=st.session_state.relaxed_answers[current_q],
        key=f"relaxed_q{current_q}"
    )

def display_results():
    if not st.session_state.relaxed_completed:
        st.error("Please complete both survey modes first.")
        st.session_state.current_mode = "timer" if not st.session_state.timer_completed else "relaxed"
        st.rerun()
        return
    
    st.header("Survey Results")
    
    # Create DataFrame for results
    results = []
    for i in range(len(st.session_state.questions)):
        results.append({
            "Question": st.session_state.questions[i],
            "Timer Mode Answer": st.session_state.timer_answers[i],
            "Relaxed Mode Answer": st.session_state.relaxed_answers[i],
            "Time Spent in Relaxed Mode (seconds)": round(st.session_state.relaxed_times[i], 1)
        })
    
    results_df = pd.DataFrame(results)
    st.dataframe(results_df)
    
    # Option to download results
    csv = results_df.to_csv(index=False)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    st.download_button(
        label="Download Results as CSV",
        data=csv,
        file_name=f"survey_results_{timestamp}.csv",
        mime="text/csv"
    )
    
    # Option to restart survey
    if st.button("Start New Survey"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

if __name__ == "__main__":
    main()