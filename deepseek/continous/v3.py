import streamlit as st
import time
from datetime import datetime
import pandas as pd

# Set Streamlit version explicitly (though actual version depends on user's environment)
st.set_page_config(page_title="Survey App", layout="wide")

# Define survey questions and options
SURVEY_QUESTIONS = [
    {
        "question": "How often do you use Python for your work?",
        "options": ["Daily", "Weekly", "Monthly", "Rarely", "Never"]
    },
    {
        "question": "Which Python web framework do you prefer?",
        "options": ["Django", "Flask", "FastAPI", "Streamlit", "Other"]
    },
    {
        "question": "How would you rate your Python expertise?",
        "options": ["Beginner", "Intermediate", "Advanced", "Expert"]
    },
    {
        "question": "What type of applications do you build most often?",
        "options": ["Web Apps", "Data Analysis", "Machine Learning", "Scripting", "Other"]
    }
]

class SurveyApp:
    def __init__(self):
        self.initialize_session_state()
        
    def initialize_session_state(self):
        """Initialize all required session state variables"""
        if 'current_mode' not in st.session_state:
            st.session_state.current_mode = "timer"
            
        if 'current_question' not in st.session_state:
            st.session_state.current_question = 0
            
        if 'timer_start' not in st.session_state:
            st.session_state.timer_start = time.time()
            
        if 'timer_duration' not in st.session_state:
            st.session_state.timer_duration = 15  # seconds per question in timer mode
            
        if 'timer_answers' not in st.session_state:
            st.session_state.timer_answers = {}
            
        if 'relaxed_answers' not in st.session_state:
            st.session_state.relaxed_answers = {}
            
        if 'relaxed_start_times' not in st.session_state:
            st.session_state.relaxed_start_times = {}
            
        if 'relaxed_time_spent' not in st.session_state:
            st.session_state.relaxed_time_spent = {}
            
        if 'survey_complete' not in st.session_state:
            st.session_state.survey_complete = False
            
        if 'timer_complete' not in st.session_state:
            st.session_state.timer_complete = False
            
    def reset_timer(self):
        """Reset the timer for the current question"""
        st.session_state.timer_start = time.time()
        
    def calculate_time_remaining(self):
        """Calculate remaining time for the current question"""
        elapsed = time.time() - st.session_state.timer_start
        remaining = max(0, st.session_state.timer_duration - elapsed)
        return remaining
        
    def render_timer_bar(self):
        """Render the shrinking timer bar"""
        remaining = self.calculate_time_remaining()
        progress = remaining / st.session_state.timer_duration
        progress_bar = st.progress(progress)
        
        # Update the progress bar in real-time
        while remaining > 0 and st.session_state.current_mode == "timer":
            remaining = self.calculate_time_remaining()
            progress = remaining / st.session_state.timer_duration
            progress_bar.progress(progress)
            time.sleep(0.1)
            
        # If we got here and we're still in timer mode, time's up - move to next question
        if st.session_state.current_mode == "timer":
            self.next_question()
            
    def next_question(self):
        """Move to the next question or end timer mode"""
        if st.session_state.current_question < len(SURVEY_QUESTIONS) - 1:
            st.session_state.current_question += 1
            self.reset_timer()
            st.rerun()
        else:
            st.session_state.timer_complete = True
            st.rerun()
            
    def prev_question(self):
        """Move to the previous question (only in relaxed mode)"""
        if st.session_state.current_question > 0:
            # Record time spent on current question before moving back
            self.record_time_spent()
            st.session_state.current_question -= 1
            st.rerun()
            
    def record_time_spent(self):
        """Record time spent on current question in relaxed mode"""
        if st.session_state.current_mode == "relaxed":
            current_q = st.session_state.current_question
            if current_q in st.session_state.relaxed_start_times:
                time_spent = time.time() - st.session_state.relaxed_start_times[current_q]
                st.session_state.relaxed_time_spent[current_q] = time_spent
                
    def start_relaxed_mode(self):
        """Switch to relaxed mode"""
        if st.session_state.timer_complete:
            st.session_state.current_mode = "relaxed"
            st.session_state.current_question = 0
            # Initialize start times for all questions
            for i in range(len(SURVEY_QUESTIONS)):
                st.session_state.relaxed_start_times[i] = time.time()
            st.rerun()
            
    def complete_survey(self):
        """Mark survey as complete"""
        self.record_time_spent()  # Record time for last question
        st.session_state.survey_complete = True
        st.rerun()
        
    def render_timer_mode(self):
        """Render the timer mode interface"""
        st.header("Survey - Timer Mode")
        st.warning("You are in TIMER mode. Answer quickly - the timer is running!")
        
        current_q = st.session_state.current_question
        question_data = SURVEY_QUESTIONS[current_q]
        
        st.subheader(f"Question {current_q + 1}/{len(SURVEY_QUESTIONS)}")
        st.markdown(f"**{question_data['question']}**")
        
        # Render the timer bar (this will handle its own updates)
        self.render_timer_bar()
        
        # Store the answer if user selects one
        selected_option = st.radio(
            "Select your answer:",
            question_data["options"],
            key=f"timer_q{current_q}"
        )
        
        if selected_option:
            st.session_state.timer_answers[current_q] = selected_option
            
        # Next button (optional since timer will auto-advance)
        if st.button("Next Question"):
            self.next_question()
            
    def render_relaxed_mode(self):
        """Render the relaxed mode interface"""
        st.header("Survey - Relaxed Mode")
        st.success("You are in RELAXED mode. Take your time to review your answers.")
        
        current_q = st.session_state.current_question
        question_data = SURVEY_QUESTIONS[current_q]
        
        st.subheader(f"Question {current_q + 1}/{len(SURVEY_QUESTIONS)}")
        st.markdown(f"**{question_data['question']}**")
        
        # Show the answer given in timer mode
        timer_answer = st.session_state.timer_answers.get(current_q, "Not answered")
        st.info(f"Your timer mode answer: {timer_answer}")
        
        # Store the answer if user selects one
        selected_option = st.radio(
            "Select your answer:",
            question_data["options"],
            index=question_data["options"].index(timer_answer) if timer_answer in question_data["options"] else 0,
            key=f"relaxed_q{current_q}"
        )
        
        if selected_option:
            st.session_state.relaxed_answers[current_q] = selected_option
            
        # Navigation buttons
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            if current_q > 0:
                if st.button("Previous Question"):
                    self.prev_question()
                    
        with col2:
            if current_q < len(SURVEY_QUESTIONS) - 1:
                if st.button("Next Question"):
                    self.record_time_spent()
                    st.session_state.current_question += 1
                    st.session_state.relaxed_start_times[st.session_state.current_question] = time.time()
                    st.rerun()
            else:
                if st.button("Complete Survey"):
                    self.complete_survey()
                    
    def render_results(self):
        """Render the survey results"""
        st.header("Survey Complete!")
        st.success("Thank you for completing the survey. Here are your results:")
        
        # Prepare data for display
        results = []
        for i, question in enumerate(SURVEY_QUESTIONS):
            results.append({
                "Question": question["question"],
                "Timer Answer": st.session_state.timer_answers.get(i, "Not answered"),
                "Relaxed Answer": st.session_state.relaxed_answers.get(i, "Not answered"),
                "Time Spent (Relaxed)": f"{st.session_state.relaxed_time_spent.get(i, 0):.1f} seconds"
            })
            
        st.dataframe(pd.DataFrame(results))
        
        # Download button
        csv = pd.DataFrame(results).to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Results as CSV",
            data=csv,
            file_name="survey_results.csv",
            mime="text/csv"
        )
        
    def run(self):
        """Main application controller"""
        # Sidebar with mode information
        with st.sidebar:
            st.header("Survey Modes")
            if st.session_state.current_mode == "timer":
                st.error("Current Mode: TIMER")
                remaining = self.calculate_time_remaining()
                st.write(f"Time remaining: {remaining:.1f} seconds")
                
                if st.session_state.timer_complete:
                    st.success("Timer mode complete! Proceed to relaxed mode.")
                    if st.button("Start Relaxed Mode"):
                        self.start_relaxed_mode()
                else:
                    st.warning("You must complete all questions in timer mode before proceeding.")
                    
            elif st.session_state.current_mode == "relaxed":
                st.success("Current Mode: RELAXED")
                current_q = st.session_state.current_question
                if current_q in st.session_state.relaxed_start_times:
                    time_spent = time.time() - st.session_state.relaxed_start_times[current_q]
                    st.write(f"Time spent on this question: {time_spent:.1f} seconds")
                    
            elif st.session_state.survey_complete:
                st.success("Survey Complete!")
                
        # Main content area
        if st.session_state.survey_complete:
            self.render_results()
        elif st.session_state.current_mode == "timer":
            self.render_timer_mode()
        elif st.session_state.current_mode == "relaxed":
            self.render_relaxed_mode()
            
# Run the app
if __name__ == "__main__":
    app = SurveyApp()
    app.run()