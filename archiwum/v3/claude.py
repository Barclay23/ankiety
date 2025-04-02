import streamlit as st
import time
import pandas as pd
import json
from datetime import datetime
import os

class SurveyApp:
    def __init__(self):
        # Initialize session state variables if they don't exist
        if 'initialized' not in st.session_state:
            st.session_state.initialized = True
            st.session_state.mode = "timer"  # Start in timer mode
            st.session_state.current_question = 0
            st.session_state.timer_answers = {}
            st.session_state.relaxed_answers = {}
            st.session_state.question_start_time = None
            st.session_state.relaxed_time_spent = {}
            st.session_state.timer_complete = False
            st.session_state.timer_mode_started = False
            st.session_state.time_per_question = 30  # Default time limit in seconds
            st.session_state.last_update_time = time.time()
            
        # Sample questions (can be loaded from external file)
        self.questions = [
            {
                "id": 1,
                "text": "Which programming language is known for its use in data science?",
                "options": ["Java", "Python", "C++", "Ruby"],
                "correct": "Python"
            },
            {
                "id": 2,
                "text": "What does HTML stand for?",
                "options": ["Hyper Text Markup Language", "High Tech Multi Language", "Hyper Transfer Markup Language", "Hierarchical Text Markup Language"],
                "correct": "Hyper Text Markup Language"
            },
            {
                "id": 3,
                "text": "Which of these is NOT a cloud computing service provider?",
                "options": ["Amazon Web Services", "Microsoft Azure", "Oracle Cloud", "Adobe Cloud"],
                "correct": "Adobe Cloud"
            },
            {
                "id": 4,
                "text": "What year was the first iPhone released?",
                "options": ["2005", "2006", "2007", "2008"],
                "correct": "2007"
            },
            {
                "id": 5,
                "text": "Which of these is a NoSQL database?",
                "options": ["MySQL", "PostgreSQL", "MongoDB", "SQLite"],
                "correct": "MongoDB"
            }
        ]

    def run(self):
        """Main application entry point"""
        st.title("Advanced Survey Application")
        
        # Display current mode
        mode_label = "Timer Mode" if st.session_state.mode == "timer" else "Relaxed Mode"
        st.subheader(f"Current Mode: {mode_label}")
        
        # Show configuration options before timer mode starts
        if not st.session_state.timer_mode_started and st.session_state.mode == "timer":
            self.show_config()
        # Show appropriate view based on current mode
        elif st.session_state.mode == "timer":
            self.timer_mode()
        else:
            self.relaxed_mode()
            
        # Show debug info in sidebar (can be removed in production)
        with st.sidebar:
            st.write("### Debug Information")
            st.write(f"Current Mode: {st.session_state.mode}")
            st.write(f"Current Question: {st.session_state.current_question + 1}/{len(self.questions)}")
            st.write(f"Timer Complete: {st.session_state.timer_complete}")
            
            if st.button("Export Results"):
                self.export_results()

    def show_config(self):
        """Configuration screen before starting timer mode"""
        st.write("### Timer Mode Configuration")
        st.write("Set the time limit per question before starting the survey.")
        
        st.session_state.time_per_question = st.slider(
            "Time per question (seconds)", 
            min_value=10, 
            max_value=120, 
            value=st.session_state.time_per_question,
            step=5
        )
        
        st.write(f"You will have {st.session_state.time_per_question} seconds to answer each question.")
        st.write("Once timer mode is completed, you will proceed to relaxed mode to review your answers.")
        
        if st.button("Start Timer Mode", type="primary"):
            st.session_state.timer_mode_started = True
            st.session_state.question_start_time = time.time()
            st.experimental_rerun()

    def timer_mode(self):
        """Display questions with a timer"""
        if st.session_state.current_question >= len(self.questions):
            # All timer questions completed
            st.session_state.timer_complete = True
            st.session_state.mode = "relaxed"
            st.session_state.current_question = 0
            st.experimental_rerun()
            return
            
        # Get current question
        question = self.questions[st.session_state.current_question]
        
        # Display remaining time
        if st.session_state.question_start_time is not None:
            elapsed_time = time.time() - st.session_state.question_start_time
            remaining_time = max(0, st.session_state.time_per_question - elapsed_time)
            
            # Update the progress bar only if 0.1 second has passed since last update
            # This prevents excessive reruns
            if time.time() - st.session_state.last_update_time > 0.1:
                st.session_state.last_update_time = time.time()
                
            progress = 1 - (remaining_time / st.session_state.time_per_question)
            
            # Change color based on remaining time
            color = "red" if remaining_time < 5 else "orange" if remaining_time < 10 else "blue"
            st.markdown(f"<div style='color:{color}; font-size:24px; font-weight:bold;'>{int(remaining_time)} seconds remaining</div>", unsafe_allow_html=True)
            st.progress(min(1.0, progress))
            
            # Auto-advance when time is up
            if remaining_time <= 0:
                st.session_state.current_question += 1
                st.session_state.question_start_time = time.time()
                st.experimental_rerun()
                return
                
        # Display question and options
        self.display_question(question, mode="timer")
        
        # Button to submit answer
        col1, col2 = st.columns([1, 5])
        with col1:
            if st.button("Next", key=f"timer_next_{question['id']}"):
                st.session_state.current_question += 1
                st.session_state.question_start_time = time.time()
                st.experimental_rerun()

    def relaxed_mode(self):
        """Display questions without a timer and with navigation"""
        if not st.session_state.timer_complete:
            st.error("You must complete the timer mode first!")
            return
            
        # Navigation controls
        st.write("### Question Navigation")
        col1, col2, col3 = st.columns([1, 1, 3])
        
        with col1:
            if st.button("← Previous") and st.session_state.current_question > 0:
                # Save time spent on current question before moving
                if st.session_state.question_start_time:
                    question_id = self.questions[st.session_state.current_question]['id']
                    time_spent = time.time() - st.session_state.question_start_time
                    st.session_state.relaxed_time_spent[question_id] = time_spent
                
                st.session_state.current_question -= 1
                st.session_state.question_start_time = time.time()
                st.experimental_rerun()
                
        with col2:
            if st.button("Next →") and st.session_state.current_question < len(self.questions) - 1:
                # Save time spent on current question before moving
                if st.session_state.question_start_time:
                    question_id = self.questions[st.session_state.current_question]['id']
                    time_spent = time.time() - st.session_state.question_start_time
                    st.session_state.relaxed_time_spent[question_id] = time_spent
                
                st.session_state.current_question += 1
                st.session_state.question_start_time = time.time()
                st.experimental_rerun()
                
        # Display question index
        st.write(f"Question {st.session_state.current_question + 1} of {len(self.questions)}")
        
        # Get current question
        question = self.questions[st.session_state.current_question]
        
        # Start timing if not already started
        if st.session_state.question_start_time is None:
            st.session_state.question_start_time = time.time()
            
        # Display question and options
        self.display_question(question, mode="relaxed")
        
        # Complete survey button on last question
        if st.session_state.current_question == len(self.questions) - 1:
            if st.button("Complete Survey", type="primary"):
                # Save time for the last question
                question_id = self.questions[st.session_state.current_question]['id']
                time_spent = time.time() - st.session_state.question_start_time
                st.session_state.relaxed_time_spent[question_id] = time_spent
                
                self.show_results()

    def display_question(self, question, mode):
        """Display a question with its options"""
        st.write(f"### Question {question['id']}: {question['text']}")
        
        # Determine which session state to use based on mode
        answers_dict = st.session_state.timer_answers if mode == "timer" else st.session_state.relaxed_answers
        
        # Create a radio button for the options
        selected_option = st.radio(
            "Choose an answer:",
            question['options'],
            key=f"{mode}_{question['id']}",
            index=None if question['id'] not in answers_dict else question['options'].index(answers_dict[question['id']])
        )
        
        # Store the answer if one is selected
        if selected_option:
            answers_dict[question['id']] = selected_option
            
        # If in timer mode, show previous answer if available
        if mode == "relaxed" and question['id'] in st.session_state.timer_answers:
            st.info(f"Your answer in timer mode: {st.session_state.timer_answers[question['id']]}")

    def show_results(self):
        """Display the results of both modes"""
        st.title("Survey Results")
        
        # Create comparison table
        results = []
        for question in self.questions:
            timer_answer = st.session_state.timer_answers.get(question['id'], "Not answered")
            relaxed_answer = st.session_state.relaxed_answers.get(question['id'], "Not answered")
            relaxed_time = st.session_state.relaxed_time_spent.get(question['id'], 0)
            
            results.append({
                "Question": question['text'],
                "Timer Mode Answer": timer_answer,
                "Relaxed Mode Answer": relaxed_answer,
                "Time Spent (Relaxed Mode)": f"{relaxed_time:.1f} seconds",
                "Correct Answer": question['correct']
            })
            
        # Convert to DataFrame for display
        df = pd.DataFrame(results)
        st.table(df)
        
        # Calculate scores
        timer_correct = sum(1 for q in self.questions if 
                            q['id'] in st.session_state.timer_answers and 
                            st.session_state.timer_answers[q['id']] == q['correct'])
                            
        relaxed_correct = sum(1 for q in self.questions if 
                              q['id'] in st.session_state.relaxed_answers and 
                              st.session_state.relaxed_answers[q['id']] == q['correct'])
        
        # Display scores
        st.write(f"### Timer Mode Score: {timer_correct}/{len(self.questions)}")
        st.write(f"### Relaxed Mode Score: {relaxed_correct}/{len(self.questions)}")
        
        # Export button
        if st.button("Export Results as JSON"):
            self.export_results()

    def export_results(self):
        """Export survey results to a JSON file"""
        results = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "timer_answers": st.session_state.timer_answers,
            "relaxed_answers": st.session_state.relaxed_answers,
            "relaxed_time_spent": {str(k): v for k, v in st.session_state.relaxed_time_spent.items()},
            "questions": self.questions
        }
        
        # Create results directory if it doesn't exist
        os.makedirs("results", exist_ok=True)
        
        # Generate filename with timestamp
        filename = f"results/survey_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Write to file
        with open(filename, "w") as f:
            json.dump(results, f, indent=4)
            
        st.success(f"Results exported to {filename}")

# Main entry point
if __name__ == "__main__":
    app = SurveyApp()
    app.run()