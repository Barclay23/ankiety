import streamlit as st
import time
import pandas as pd

# Set page configuration
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
        defaults = {
            'current_mode': "timer",
            'current_question': 0,
            'timer_start': time.time(),
            'timer_duration': 15,  # seconds per question
            'timer_answers': {i: "" for i in range(len(SURVEY_QUESTIONS))},  # Pre-initialize
            'relaxed_answers': {i: "" for i in range(len(SURVEY_QUESTIONS))},
            'relaxed_start_times': {},
            'relaxed_time_spent': {},
            'survey_complete': False,
            'timer_complete': False,
            'force_rerun': False
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
        """Render the shrinking timer bar with improved state handling"""
        remaining = self.calculate_time_remaining()
        progress = remaining / st.session_state.timer_duration
        progress_bar = st.progress(progress)
        
        # Update the progress bar in real-time
        while remaining > 0 and st.session_state.current_mode == "timer":
            remaining = self.calculate_time_remaining()
            progress = remaining / st.session_state.timer_duration
            progress_bar.progress(progress)
            time.sleep(0.1)
            
            if st.session_state.force_rerun:
                progress_bar.empty()
                return
            
        if (remaining <= 0 and st.session_state.current_mode == "timer" 
            and not st.session_state.force_rerun):
            progress_bar.empty()
            self.next_question()
            
    def next_question(self):
        """Move to the next question or end timer mode"""
        current_q = st.session_state.current_question
        
        # Store the current answer before moving
        if f"timer_q{current_q}" in st.session_state:
            st.session_state.timer_answers[current_q] = st.session_state[f"timer_q{current_q}"]
        
        if current_q < len(SURVEY_QUESTIONS) - 1:
            st.session_state.current_question += 1
            self.reset_timer()
            st.session_state.force_rerun = False
            st.rerun()
        else:
            st.session_state.timer_complete = True
            self.start_relaxed_mode()  # Auto transition
            
    def prev_question(self):
        """Move to the previous question (only in relaxed mode)"""
        if st.session_state.current_question > 0:
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
        """Automatically switch to relaxed mode when timer completes"""
        st.session_state.current_mode = "relaxed"
        st.session_state.current_question = 0
        
        # Initialize relaxed answers with timer answers
        for i in range(len(SURVEY_QUESTIONS)):
            st.session_state.relaxed_answers[i] = st.session_state.timer_answers[i]
            st.session_state.relaxed_start_times[i] = time.time()
            
        st.rerun()
        
    def complete_survey(self):
        """Mark survey as complete"""
        self.record_time_spent()
        st.session_state.survey_complete = True
        st.rerun()
        
    def render_timer_mode(self):
        """Render timer mode with properly displayed answers"""
        st.header("Survey - Timer Mode")
        st.warning("You are in TIMER mode. Answer quickly - the timer is running!")
        
        current_q = st.session_state.current_question
        question_data = SURVEY_QUESTIONS[current_q]
        
        st.subheader(f"Question {current_q + 1}/{len(SURVEY_QUESTIONS)}")
        st.markdown(f"**{question_data['question']}**")
        
        # Get current answer or empty string if not answered
        current_answer = st.session_state.timer_answers[current_q]
        
        # Display radio buttons with current selection
        selected_option = st.radio(
            "Select your answer:",
            question_data["options"],
            key=f"timer_q{current_q}",
            index=question_data["options"].index(current_answer) if current_answer in question_data["options"] else 0
        )
        
        # Store selection immediately
        st.session_state.timer_answers[current_q] = selected_option
        
        # Render timer bar
        self.render_timer_bar()
            
        # Next button
        if st.button("Next Question"):
            st.session_state.force_rerun = True
            self.next_question()
            
    def render_relaxed_mode(self):
        """Render relaxed mode interface"""
        st.header("Survey - Relaxed Mode")
        st.success("You are in RELAXED mode. Take your time to review your answers.")
        
        current_q = st.session_state.current_question
        question_data = SURVEY_QUESTIONS[current_q]
        
        st.subheader(f"Question {current_q + 1}/{len(SURVEY_QUESTIONS)}")
        st.markdown(f"**{question_data['question']}**")
        
        # Show timer mode answer
        timer_answer = st.session_state.timer_answers.get(current_q, "Not answered")
        st.info(f"Your timer mode answer: {timer_answer}")
        
        # Get current relaxed answer
        current_answer = st.session_state.relaxed_answers[current_q]
        
        # Display radio buttons
        selected_option = st.radio(
            "Select your answer:",
            question_data["options"],
            index=question_data["options"].index(current_answer) if current_answer in question_data["options"] else 0,
            key=f"relaxed_q{current_q}"
        )
        
        # Store selection
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
        """Render survey results"""
        st.header("Survey Complete!")
        st.success("Thank you for completing the survey. Here are your results:")
        
        results = []
        answer_changes = 0
        
        for i, question in enumerate(SURVEY_QUESTIONS):
            timer_answer = st.session_state.timer_answers.get(i, "Not answered")
            relaxed_answer = st.session_state.relaxed_answers.get(i, "Not answered")
            
            if timer_answer != relaxed_answer:
                answer_changes += 1
                
            results.append({
                "Question": question["question"],
                "Timer Answer": timer_answer,
                "Relaxed Answer": relaxed_answer,
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
        # Sidebar
        with st.sidebar:
            st.header("Survey Modes")
            if st.session_state.current_mode == "timer":
                st.error("Current Mode: TIMER")
                remaining = self.calculate_time_remaining()
                st.write(f"Time remaining: {remaining:.1f} seconds")
                
            elif st.session_state.current_mode == "relaxed":
                st.success("Current Mode: RELAXED")
                current_q = st.session_state.current_question
                if current_q in st.session_state.relaxed_start_times:
                    time_spent = time.time() - st.session_state.relaxed_start_times[current_q]
                    st.write(f"Time spent: {time_spent:.1f} seconds")
                    
            elif st.session_state.survey_complete:
                st.success("Survey Complete!")
                
        # Main content
        if st.session_state.survey_complete:
            self.render_results()
        elif st.session_state.current_mode == "timer":
            self.render_timer_mode()
        elif st.session_state.current_mode == "relaxed":
            self.render_relaxed_mode()
            
if __name__ == "__main__":
    app = SurveyApp()
    app.run()