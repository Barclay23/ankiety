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
        """Initialize all required session state variables with proper type hints"""
        defaults = {
            'current_mode': "timer",
            'current_question': 0,
            'timer_start': time.time(),
            'timer_duration': 15,  # seconds per question in timer mode
            'timer_answers': {},
            'relaxed_answers': {},
            'relaxed_start_times': {},
            'relaxed_time_spent': {},
            'survey_complete': False,
            'timer_complete': False,
            'force_rerun': False  # Flag to control manual reruns
        }
        
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value
        
    def reset_timer(self):
        """Reset the timer for the current question"""
        st.session_state.timer_start = time.time()
        
    def calculate_time_remaining(self):
        """Calculate remaining time for the current question"""
        elapsed = time.time() - st.session_state.timer_start
        return max(0, st.session_state.timer_duration - elapsed)
        
    def render_timer_bar(self):
        """Render the shrinking timer bar with improved performance"""
        remaining = self.calculate_time_remaining()
        progress = remaining / st.session_state.timer_duration
        progress_bar = st.progress(progress)
        
        # Update the progress bar in real-time
        while remaining > 0 and st.session_state.current_mode == "timer":
            remaining = self.calculate_time_remaining()
            progress = remaining / st.session_state.timer_duration
            progress_bar.progress(progress)
            time.sleep(0.1)
            
            # Check if user has manually advanced to next question
            if st.session_state.force_rerun:
                progress_bar.empty()
                return
            
        # Only proceed if we're still in timer mode (not manually advanced)
        if (remaining <= 0 and st.session_state.current_mode == "timer" 
            and not st.session_state.force_rerun):
            self.next_question()
            
    def next_question(self):
        """Move to the next question or end timer mode"""
        current_q = st.session_state.current_question
        question_data = SURVEY_QUESTIONS[current_q]
        
        # Store the selected answer if available
        selected_option = st.session_state.get(f"timer_q{current_q}")
        if selected_option:
            st.session_state.timer_answers[current_q] = selected_option
        
        if current_q < len(SURVEY_QUESTIONS) - 1:
            st.session_state.current_question += 1
            self.reset_timer()
            st.session_state.force_rerun = False
            st.rerun()
        else:
            st.session_state.timer_complete = True
            st.session_state.force_rerun = False
            self.start_relaxed_mode()  # Automatically transition to relaxed mode
            
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
        """Switch to relaxed mode automatically when timer mode completes"""
        st.session_state.current_mode = "relaxed"
        st.session_state.current_question = 0
        
        # Initialize answers from timer mode if not already set
        for i in range(len(SURVEY_QUESTIONS)):
            st.session_state.relaxed_answers[i] = st.session_state.timer_answers.get(i, "")
            st.session_state.relaxed_start_times[i] = time.time()
            
        st.rerun()
        
    def complete_survey(self):
        """Mark survey as complete"""
        self.record_time_spent()  # Record time for last question
        st.session_state.survey_complete = True
        st.rerun()
        
    def render_timer_mode(self):
        """Render the timer mode interface with improved answer handling"""
        st.header("Survey - Timer Mode")
        st.warning("You are in TIMER mode. Answer quickly - the timer is running!")
        
        current_q = st.session_state.current_question
        question_data = SURVEY_QUESTIONS[current_q]
        
        st.subheader(f"Question {current_q + 1}/{len(SURVEY_QUESTIONS)}")
        st.markdown(f"**{question_data['question']}**")
        
        # Store the answer if user selects one
        selected_option = st.radio(
            "Select your answer:",
            question_data["options"],
            key=f"timer_q{current_q}",
            index=question_data["options"].index(
                st.session_state.timer_answers.get(current_q, "")
            ) if st.session_state.timer_answers.get(current_q, "") in question_data["options"] else 0
        )
        
        if selected_option:
            st.session_state.timer_answers[current_q] = selected_option
            
        # Render the timer bar (this will handle its own updates)
        self.render_timer_bar()
            
        # Next button with manual advance control
        if st.button("Next Question"):
            st.session_state.force_rerun = True
            self.next_question()
            
    def render_relaxed_mode(self):
        """Render the relaxed mode interface with improved navigation"""
        st.header("Survey - Relaxed Mode")
        st.success("You are in RELAXED mode. Take your time to review your answers.")
        
        current_q = st.session_state.current_question
        question_data = SURVEY_QUESTIONS[current_q]
        
        st.subheader(f"Question {current_q + 1}/{len(SURVEY_QUESTIONS)}")
        st.markdown(f"**{question_data['question']}**")
        
        # Show the answer given in timer mode
        timer_answer = st.session_state.timer_answers.get(current_q, "Not answered")
        st.info(f"Your timer mode answer: {timer_answer}")
        
        # Get current answer or default to timer answer
        current_answer = st.session_state.relaxed_answers.get(current_q, timer_answer)
        
        # Store the answer if user selects one
        selected_option = st.radio(
            "Select your answer:",
            question_data["options"],
            index=question_data["options"].index(current_answer) if current_answer in question_data["options"] else 0,
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
        """Render the survey results with enhanced display"""
        st.header("Survey Complete!")
        st.success("Thank you for completing the survey. Here are your results:")
        
        # Prepare data for display with additional analysis
        results = []
        answer_changes = 0
        
        for i, question in enumerate(SURVEY_QUESTIONS):
            timer_answer = st.session_state.timer_answers.get(i, "Not answered")
            relaxed_answer = st.session_state.relaxed_answers.get(i, "Not answered")
            
            if timer_answer != relaxed_answer:
                answer_changes += 1
                
            results.append({
                "Question Number": i + 1,
                "Question": question["question"],
                "Timer Answer": timer_answer,
                "Relaxed Answer": relaxed_answer,
                "Answer Changed": "Yes" if timer_answer != relaxed_answer else "No",
                "Time Spent (Relaxed)": f"{st.session_state.relaxed_time_spent.get(i, 0):.1f} seconds"
            })
            
        df = pd.DataFrame(results)
        st.dataframe(df)
        
        # Show summary statistics
        st.subheader("Summary Statistics")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Questions", len(SURVEY_QUESTIONS))
            st.metric("Questions Changed in Relaxed Mode", answer_changes)
            
        with col2:
            avg_time = df["Time Spent (Relaxed)"].str.extract(r'(\d+\.\d+)')[0].astype(float).mean()
            st.metric("Average Time per Question (Relaxed)", f"{avg_time:.1f} seconds")
        
        # Download button
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Results as CSV",
            data=csv,
            file_name="survey_results.csv",
            mime="text/csv"
        )
        
    def run(self):
        """Main application controller with improved state management"""
        # Sidebar with mode information
        with st.sidebar:
            st.header("Survey Modes")
            if st.session_state.current_mode == "timer":
                st.error("Current Mode: TIMER")
                remaining = self.calculate_time_remaining()
                st.write(f"Time remaining: {remaining:.1f} seconds")
                
                if st.session_state.timer_complete:
                    st.success("Timer mode complete! Switching to relaxed mode...")
                    
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