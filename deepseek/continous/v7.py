import streamlit as st
import time
import pandas as pd

# Set page configuration with custom colors
st.set_page_config(page_title="Survey App", layout="wide")

# Custom CSS for blue background and white text
st.markdown(
    """
    <style>
    .stApp {
        background-color: #1E3F8B;
        color: white;
    }
    .st-bq, .st-c0, .st-c1, .st-c2, .st-c3, .st-c4, .st-c5, .st-c6, .st-c7, .st-c8, .st-c9, .st-ca, .st-cb, .st-cc, .st-cd, .st-ce, .st-cf, .st-cg, .st-ch, .st-ci, .st-cj, .st-ck, .st-cl, .st-cm, .st-cn, .st-co, .st-cp, .st-cq, .st-cr, .st-cs, .st-ct, .st-cu, .st-cv, .st-cw, .st-cx, .st-cy, .st-cz {
        color: white;
    }
    .stRadio > div > div > label, .stCheckbox > label {
        color: white !important;
    }
    .stButton > button {
        color: white;
        border-color: white;
    }
    .stProgress > div > div > div > div {
        background-color: #4CAF50;
    }
    .stDataFrame {
        background-color: white;
        color: black;
    }
    .stAlert {
        background-color: rgba(255, 255, 255, 0.1);
    }
    .stTextInput > div > div > input, .stTextArea > div > div > textarea {
        color: black;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Define survey questions with different types
SURVEY_QUESTIONS = [
    {
        "type": "multiple_choice_single",
        "question": "How often do you use Python for your work?",
        "options": ["Daily", "Weekly", "Monthly", "Rarely", "Never"]
    },
    {
        "type": "multiple_choice_multi",
        "question": "Which Python web frameworks do you use? (Select all that apply)",
        "options": ["Django", "Flask", "FastAPI", "Streamlit", "Other"]
    },
    {
        "type": "open_ended",
        "question": "What do you enjoy most about Python programming?",
        "placeholder": "Enter your thoughts here..."
    },
    {
        "type": "multiple_choice_single",
        "question": "How would you rate your Python expertise?",
        "options": ["Beginner", "Intermediate", "Advanced", "Expert"]
    },
    {
        "type": "multiple_choice_multi", 
        "question": "What Python concepts are you most comfortable with?",
        "options": ["Object-oriented programming", "Functional programming", 
                   "Decorators", "Generators", "Context managers", "Async/await"]
    },
    {
        "type": "open_ended",
        "question": "Describe a challenging Python project you've worked on:",
        "placeholder": "Share your experience..."
    },
    {
        "type": "multiple_choice_multi",
        "question": "What types of applications do you build with Python?",
        "options": ["Web Apps", "Data Analysis", "Machine Learning", 
                   "Scripting", "Automation", "Other"]
    }
]

class SurveyApp:
    def __init__(self):
        self.initialize_session_state()
        
    def initialize_session_state(self):
        """Initialize all required session state variables with proper defaults"""
        defaults = {
            'current_mode': "timer",
            'current_question': 0,
            'timer_start': time.time(),
            'timer_duration': 15,  # seconds per question
            'timer_answers': {i: None for i in range(len(SURVEY_QUESTIONS))},
            'relaxed_answers': {i: None for i in range(len(SURVEY_QUESTIONS))},
            'relaxed_start_times': {},
            'relaxed_time_spent': {},
            'survey_complete': False,
            'timer_complete': False,
            'force_rerun': False
        }
        
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value
                
        # Initialize multi-select answers as empty lists
        for i, question in enumerate(SURVEY_QUESTIONS):
            if question["type"] == "multiple_choice_multi":
                if st.session_state.timer_answers[i] is None:
                    st.session_state.timer_answers[i] = []
                if st.session_state.relaxed_answers[i] is None:
                    st.session_state.relaxed_answers[i] = []
        
    def reset_timer(self):
        """Reset the timer for the current question"""
        st.session_state.timer_start = time.time()
        
    def calculate_time_remaining(self):
        """Calculate remaining time for the current question"""
        elapsed = time.time() - st.session_state.timer_start
        return max(0, st.session_state.timer_duration - elapsed)
        
    def render_timer_bar(self):
        """Render the shrinking timer bar with proper cleanup"""
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
            self.start_relaxed_mode()  # Auto transition to relaxed mode
            
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
        
    def format_answer_for_display(self, answer, question_type):
        """Format answers for display in results"""
        if answer is None:
            return "Not answered"
        if question_type == "multiple_choice_multi" and isinstance(answer, list):
            return ", ".join(answer) if answer else "None selected"
        return str(answer)
        
    def render_question(self, current_q, mode):
        """Render the appropriate question type based on question data"""
        question_data = SURVEY_QUESTIONS[current_q]
        
        if question_data["type"] == "multiple_choice_single":
            # Get current answer or None if not answered
            current_answer = st.session_state[f"{mode}_answers"][current_q]
            
            # Display radio buttons with current selection
            selected_option = st.radio(
                "Select your answer:",
                question_data["options"],
                key=f"{mode}_q{current_q}",
                index=question_data["options"].index(current_answer) if current_answer in question_data["options"] else 0
            )
            
            # Store selection immediately
            st.session_state[f"{mode}_answers"][current_q] = selected_option
            
        elif question_data["type"] == "multiple_choice_multi":
            # Get current answers or empty list if not answered
            current_answers = st.session_state[f"{mode}_answers"][current_q] or []
            
            # Display checkboxes with current selections
            selected_options = st.multiselect(
                "Select all that apply:",
                question_data["options"],
                default=current_answers,
                key=f"{mode}_q{current_q}"
            )
            
            # Store selections immediately
            st.session_state[f"{mode}_answers"][current_q] = selected_options
            
        elif question_data["type"] == "open_ended":
            # Get current answer or empty string if not answered
            current_answer = st.session_state[f"{mode}_answers"][current_q] or ""
            
            # Display text input with current answer
            user_input = st.text_area(
                "Your answer:",
                value=current_answer,
                key=f"{mode}_q{current_q}",
                placeholder=question_data.get("placeholder", "")
            )
            
            # Store answer immediately
            st.session_state[f"{mode}_answers"][current_q] = user_input
        
    def render_timer_mode(self):
        """Render timer mode with properly displayed answers"""
        st.header("Survey - Timer Mode")
        st.warning("You are in TIMER mode. Answer quickly - the timer is running!")
        
        current_q = st.session_state.current_question
        question_data = SURVEY_QUESTIONS[current_q]
        
        st.subheader(f"Question {current_q + 1}/{len(SURVEY_QUESTIONS)}")
        st.markdown(f"**{question_data['question']}**")
        
        # Render the appropriate question type
        self.render_question(current_q, "timer")
        
        # Render timer bar
        self.render_timer_bar()
            
        # Next button
        if st.button("Next Question"):
            st.session_state.force_rerun = True
            self.next_question()
            
    def render_relaxed_mode(self):
        """Render relaxed mode interface with proper answer tracking"""
        st.header("Survey - Relaxed Mode")
        st.success("You are in RELAXED mode. Take your time to review your answers.")
        
        current_q = st.session_state.current_question
        question_data = SURVEY_QUESTIONS[current_q]
        
        st.subheader(f"Question {current_q + 1}/{len(SURVEY_QUESTIONS)}")
        st.markdown(f"**{question_data['question']}**")
        
        # Show timer mode answer
        timer_answer = st.session_state.timer_answers.get(current_q)
        formatted_timer_answer = self.format_answer_for_display(timer_answer, question_data["type"])
        
        if question_data["type"] == "open_ended" and timer_answer:
            st.info("Your timer mode answer:")
            st.text(timer_answer)
        elif timer_answer:
            st.info(f"Your timer mode answer: {formatted_timer_answer}")
        
        # Render the appropriate question type
        self.render_question(current_q, "relaxed")
            
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
        """Render survey results with comparison between modes"""
        st.header("Survey Complete!")
        st.success("Thank you for completing the survey. Here are your results:")
        
        results = []
        answer_changes = 0
        
        for i, question in enumerate(SURVEY_QUESTIONS):
            timer_answer = st.session_state.timer_answers.get(i)
            relaxed_answer = st.session_state.relaxed_answers.get(i)
            
            formatted_timer = self.format_answer_for_display(timer_answer, question["type"])
            formatted_relaxed = self.format_answer_for_display(relaxed_answer, question["type"])
            
            if timer_answer != relaxed_answer:
                answer_changes += 1
                
            results.append({
                "Question": question["question"],
                "Type": question["type"].replace("_", " ").title(),
                "Timer Answer": formatted_timer,
                "Relaxed Answer": formatted_relaxed,
                "Changed": "Yes" if timer_answer != relaxed_answer else "No",
                "Time Spent (Relaxed)": f"{st.session_state.relaxed_time_spent.get(i, 0):.1f} seconds"
            })
            
        df = pd.DataFrame(results)
        st.dataframe(df)
        
        # Show summary statistics
        st.subheader("Summary")
        st.metric("Total Questions", len(SURVEY_QUESTIONS))
        st.metric("Answers Changed in Relaxed Mode", answer_changes)
        
        # Download button
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Results as CSV",
            data=csv,
            file_name="survey_results.csv",
            mime="text/csv"
        )
        
    def run(self):
        """Main application controller with proper state routing"""
        # Sidebar with mode information
        with st.sidebar:
            st.header("Survey Modes")
            if st.session_state.current_mode == "timer":
                st.error("Current Mode: TIMER")
                remaining = self.calculate_time_remaining()
                st.write(f"Time remaining: {remaining:.1f} seconds")
                
                if st.session_state.timer_complete:
                    st.success("Timer mode completed! Switching to relaxed mode...")
                    
            elif st.session_state.current_mode == "relaxed":
                st.success("Current Mode: RELAXED")
                current_q = st.session_state.current_question
                if current_q in st.session_state.relaxed_start_times:
                    time_spent = time.time() - st.session_state.relaxed_start_times[current_q]
                    st.write(f"Time spent: {time_spent:.1f} seconds")
                    
            elif st.session_state.survey_complete:
                st.success("Survey Complete!")
                
        # Main content routing
        if st.session_state.survey_complete:
            self.render_results()
        elif st.session_state.current_mode == "timer":
            self.render_timer_mode()
        elif st.session_state.current_mode == "relaxed":
            self.render_relaxed_mode()
            
if __name__ == "__main__":
    app = SurveyApp()
    app.run()