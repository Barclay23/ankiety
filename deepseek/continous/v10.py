import streamlit as st
import time
import pandas as pd

# Set page configuration with custom colors
st.set_page_config(page_title="Survey App", layout="wide")

# Custom CSS for improved readability and conditional styling
st.markdown(
    """
    <style>
    .stApp {
        background-color: #1E3F8B;
    }
    /* Main text color */
    body, .st-bq, .st-c0, .st-c1, .st-c2, .st-c3, .st-c4, .st-c5, .st-c6, 
    .st-c7, .st-c8, .st-c9, .st-ca, .st-cb, .st-cc, .st-cd, .st-ce, .st-cf, 
    .st-cg, .st-ch, .st-ci, .st-cj, .st-ck, .st-cl, .st-cm, .st-cn, .st-co, 
    .st-cp, .st-cq, .st-cr, .st-cs, .st-ct, .st-cu, .st-cv, .st-cw, .st-cx, 
    .st-cy, .st-cz, .stMarkdown, .stHeader, .stSubheader {
        color: #F0F0F0 !important;
    }
    
    /* Form elements */
    .stRadio > div > div > label {
        color: #F0F0F0 !important;
    }
    .stCheckbox > div > label {
        color: #F0F0F0 !important;
    }
    .stCheckbox > div > div > div {
        background-color: #F0F0F0 !important;
        border-color: #F0F0F0 !important;
    }
    .stButton > button {
        color: #1E3F8B !important;
        background-color: #F0F0F0 !important;
        border-color: #F0F0F0 !important;
    }
    .stProgress > div > div > div > div {
        background-color: #4CAF50;
    }
    
    /* Data display */
    .stDataFrame {
        background-color: white;
        color: black;
    }
    .stAlert {
        background-color: rgba(255, 255, 255, 0.15);
    }
    
    /* Input fields */
    .stTextInput > div > div > input, 
    .stTextArea > div > div > textarea {
        color: black !important;
        background-color: white !important;
    }
    
    /* Conditional question highlight */
    .conditional-question {
        background-color: rgba(76, 175, 80, 0.2);
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
    
    /* Multi-select options container */
    .stMultiSelect > div > div > div > div {
        background-color: white !important;
        color: black !important;
    }
    .stMultiSelect > div > div > div > div > div {
        color: black !important;
    }
    
    /* Style for multi-select questions */
    .multi-select-question {
        color: #FFD700 !important;  /* Gold color for multi-select questions */
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Define survey questions with strict conditional logic
SURVEY_QUESTIONS = [
    {
        "type": "multiple_choice_single",
        "question": "How often do you use Python for your work?",
        "options": ["Daily", "Weekly", "Monthly", "Rarely", "Never"],
        "conditional": {
            "trigger": "Never",
            "follow_up": {
                "type": "open_ended",
                "question": "Why don't you use Python?",
                "placeholder": "Please explain...",
                "strict": True  # Only shown if exactly "Never" is selected
            }
        }
    },
    {
        "type": "multiple_choice_single",
        "question": "Which is your primary Python web framework?",
        "options": ["Django", "Flask", "FastAPI", "Streamlit", "Other", "None"],
        "conditional": {
            "trigger": "Other",
            "follow_up": {
                "type": "open_ended",
                "question": "Please specify your primary framework:",
                "placeholder": "Framework name...",
                "strict": True
            }
        }
    },
    {
        "type": "multiple_choice_single",
        "question": "How would you rate your Python expertise?",
        "options": ["Beginner", "Intermediate", "Advanced", "Expert"],
        "conditional": {
            "trigger": "Beginner",
            "follow_up": {
                "type": "multiple_choice_single",
                "question": "What is your main learning resource?",
                "options": ["Online courses", "Books", "Documentation", 
                           "Video tutorials", "University courses"],
                "strict": True
            }
        }
    },
    {
        "type": "multiple_choice_multi", 
        "question": "What Python concepts are you familiar with?",
        "options": ["Object-oriented programming", "Functional programming", 
                   "Decorators", "Generators", "Context managers", "Async/await"]
    },
    {
        "type": "open_ended",
        "question": "Describe a challenging Python project you've worked on:",
        "placeholder": "Share your experience..."
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
            'timer_answers': {},
            'relaxed_answers': {},
            'relaxed_start_times': {},
            'relaxed_time_spent': {},
            'survey_complete': False,
            'timer_complete': False,
            'force_rerun': False,
            'active_conditional_questions': {},
            'question_flow': self.build_question_flow(),
            'last_question_change': time.time()
        }
        
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value
                
        # Initialize answer structures for all questions including conditionals
        self.initialize_answer_structures()
        
    def build_question_flow(self):
        """Build the question flow including conditional questions"""
        flow = []
        for i, question in enumerate(SURVEY_QUESTIONS):
            flow.append(i)
            if "conditional" in question:
                # Add placeholder for conditional question
                flow.append(f"conditional_{i}")
        return flow
    
    def initialize_answer_structures(self):
        """Initialize answer structures for all questions"""
        # Initialize main questions
        for i in range(len(SURVEY_QUESTIONS)):
            if i not in st.session_state.timer_answers:
                st.session_state.timer_answers[i] = None
            if i not in st.session_state.relaxed_answers:
                st.session_state.relaxed_answers[i] = None
        
        # Initialize conditional questions
        for i, question in enumerate(SURVEY_QUESTIONS):
            if "conditional" in question:
                cond_key = f"conditional_{i}"
                if cond_key not in st.session_state.timer_answers:
                    st.session_state.timer_answers[cond_key] = None
                if cond_key not in st.session_state.relaxed_answers:
                    st.session_state.relaxed_answers[cond_key] = None
                if cond_key not in st.session_state.active_conditional_questions:
                    st.session_state.active_conditional_questions[cond_key] = False
                
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
            
    def get_current_question_index(self):
        """Get the actual question index from the flow"""
        flow_pos = st.session_state.current_question
        if flow_pos >= len(st.session_state.question_flow):
            return None
        return st.session_state.question_flow[flow_pos]
    
    def is_conditional_question(self, question_ref):
        """Check if a question reference is for a conditional question"""
        return isinstance(question_ref, str) and question_ref.startswith("conditional_")
    
    def next_question(self):
        """Move to the next question or end timer mode"""
        current_flow_pos = st.session_state.current_question
        current_q_ref = st.session_state.question_flow[current_flow_pos]
        
        # Check if we need to insert a conditional question
        if not self.is_conditional_question(current_q_ref):
            current_q_index = current_q_ref
            question_data = SURVEY_QUESTIONS[current_q_index]
            
            # Check if answer triggers a conditional question
            if "conditional" in question_data and question_data["conditional"].get("strict", False):
                answer = st.session_state.timer_answers[current_q_index]
                trigger = question_data["conditional"]["trigger"]
                
                # Only show if answer exactly matches trigger (strict condition)
                should_show_conditional = answer == trigger
                
                # Update conditional question state
                cond_key = f"conditional_{current_q_index}"
                st.session_state.active_conditional_questions[cond_key] = should_show_conditional
                
                # If conditional should be shown and we're not already on it
                next_q_ref = st.session_state.question_flow[current_flow_pos + 1] if current_flow_pos + 1 < len(st.session_state.question_flow) else None
                if should_show_conditional and (not next_q_ref or next_q_ref != cond_key):
                    # Insert the conditional question into the flow
                    st.session_state.question_flow.insert(current_flow_pos + 1, cond_key)
                elif not should_show_conditional and next_q_ref == cond_key:
                    # Remove the conditional question from the flow
                    st.session_state.question_flow.pop(current_flow_pos + 1)
        
        # Move to next question
        if current_flow_pos < len(st.session_state.question_flow) - 1:
            st.session_state.current_question += 1
            self.reset_timer()
            st.session_state.force_rerun = False
            st.session_state.last_question_change = time.time()
            st.rerun()
        else:
            st.session_state.timer_complete = True
            self.start_relaxed_mode()
            
    def prev_question(self):
        """Move to the previous question (only in relaxed mode)"""
        if st.session_state.current_question > 0:
            self.record_time_spent()
            st.session_state.current_question -= 1
            st.session_state.last_question_change = time.time()
            st.rerun()
            
    def record_time_spent(self):
        """Record time spent on current question in relaxed mode"""
        if st.session_state.current_mode == "relaxed":
            current_q_ref = self.get_current_question_index()
            if current_q_ref in st.session_state.relaxed_start_times:
                time_spent = time.time() - st.session_state.relaxed_start_times[current_q_ref]
                st.session_state.relaxed_time_spent[current_q_ref] = time_spent
                st.session_state.relaxed_start_times[current_q_ref] = time.time()
                
    def start_relaxed_mode(self):
        """Automatically switch to relaxed mode when timer completes"""
        st.session_state.current_mode = "relaxed"
        st.session_state.current_question = 0
        
        # Initialize relaxed answers with timer answers
        for key in st.session_state.timer_answers:
            st.session_state.relaxed_answers[key] = st.session_state.timer_answers[key]
            st.session_state.relaxed_start_times[key] = time.time()
            
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
        
    def render_question(self, question_ref, mode):
        """Render the appropriate question type based on question data"""
        if self.is_conditional_question(question_ref):
            # This is a conditional question
            parent_index = int(question_ref.split("_")[1])
            question_data = SURVEY_QUESTIONS[parent_index]["conditional"]["follow_up"]
            container = st.container()
            container.markdown('<div class="conditional-question">', unsafe_allow_html=True)
        else:
            # Regular question
            question_data = SURVEY_QUESTIONS[question_ref]
            container = st
        
        # Get current answer
        current_answer = st.session_state[f"{mode}_answers"][question_ref]
        
        # Apply special styling for multi-select questions
        question_style = ""
        if question_data["type"] == "multiple_choice_multi":
            question_style = 'class="multi-select-question"'
        
        container.markdown(f'<div {question_style}>**{question_data["question"]}**</div>', unsafe_allow_html=True)
        
        if question_data["type"] == "multiple_choice_single":
            # Display radio buttons with current selection
            selected_option = container.radio(
                "Select your answer:",
                question_data["options"],
                key=f"{mode}_q{question_ref}",
                index=question_data["options"].index(current_answer) if current_answer in question_data["options"] else 0
            )
            
            # Store selection immediately
            st.session_state[f"{mode}_answers"][question_ref] = selected_option
            
            # Check if we need to update conditional questions in relaxed mode
            if mode == "relaxed" and not self.is_conditional_question(question_ref):
                if "conditional" in question_data and question_data["conditional"].get("strict", False):
                    cond_key = f"conditional_{question_ref}"
                    trigger = question_data["conditional"]["trigger"]
                    current_pos = st.session_state.current_question
                    
                    # Check if we need to show/hide the conditional question
                    should_show = selected_option == trigger
                    currently_showing = st.session_state.active_conditional_questions.get(cond_key, False)
                    
                    if should_show != currently_showing:
                        st.session_state.active_conditional_questions[cond_key] = should_show
                        
                        # Update the question flow if needed
                        if should_show:
                            # Insert after current question if not already there
                            if current_pos + 1 >= len(st.session_state.question_flow) or st.session_state.question_flow[current_pos + 1] != cond_key:
                                st.session_state.question_flow.insert(current_pos + 1, cond_key)
                                st.session_state.relaxed_answers[cond_key] = None
                                st.session_state.relaxed_start_times[cond_key] = time.time()
                        else:
                            # Remove if present after current question
                            if current_pos + 1 < len(st.session_state.question_flow) and st.session_state.question_flow[current_pos + 1] == cond_key:
                                st.session_state.question_flow.pop(current_pos + 1)
                        
                        # Rerun to reflect changes
                        st.rerun()
            
        elif question_data["type"] == "multiple_choice_multi":
            # Display checkboxes with current selections
            current_answers = current_answer if isinstance(current_answer, list) else []
            selected_options = container.multiselect(
                "Select all that apply:",
                question_data["options"],
                default=current_answers,
                key=f"{mode}_q{question_ref}"
            )
            
            # Store selections immediately
            st.session_state[f"{mode}_answers"][question_ref] = selected_options
            
        elif question_data["type"] == "open_ended":
            # Display text input with current answer
            current_text = current_answer if current_answer else ""
            user_input = container.text_area(
                "Your answer:",
                value=current_text,
                key=f"{mode}_q{question_ref}",
                placeholder=question_data.get("placeholder", "")
            )
            
            # Store answer immediately
            st.session_state[f"{mode}_answers"][question_ref] = user_input
        
        if self.is_conditional_question(question_ref):
            container.markdown('</div>', unsafe_allow_html=True)
        
    def render_timer_mode(self):
        """Render timer mode with properly displayed answers"""
        st.header("Survey - Timer Mode")
        st.warning("You are in TIMER mode. Answer quickly - the timer is running!")
        
        current_q_ref = self.get_current_question_index()
        
        if self.is_conditional_question(current_q_ref):
            parent_index = int(current_q_ref.split("_")[1])
            question_data = SURVEY_QUESTIONS[parent_index]["conditional"]["follow_up"]
            st.subheader(f"Follow-up Question")
        else:
            question_data = SURVEY_QUESTIONS[current_q_ref]
            st.subheader(f"Question {st.session_state.current_question + 1}/{len(st.session_state.question_flow)}")
        
        # Render the appropriate question type
        self.render_question(current_q_ref, "timer")
        
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
        
        current_q_ref = self.get_current_question_index()
        
        if self.is_conditional_question(current_q_ref):
            parent_index = int(current_q_ref.split("_")[1])
            question_data = SURVEY_QUESTIONS[parent_index]["conditional"]["follow_up"]
            st.subheader(f"Follow-up Question")
        else:
            question_data = SURVEY_QUESTIONS[current_q_ref]
            st.subheader(f"Question {st.session_state.current_question + 1}/{len(st.session_state.question_flow)}")
        
        # Show timer mode answer
        timer_answer = st.session_state.timer_answers.get(current_q_ref)
        formatted_timer_answer = self.format_answer_for_display(timer_answer, question_data["type"])
        
        if question_data["type"] == "open_ended" and timer_answer:
            st.info("Your timer mode answer:")
            st.text(timer_answer)
        elif timer_answer:
            st.info(f"Your timer mode answer: {formatted_timer_answer}")
        
        # Render the appropriate question type
        self.render_question(current_q_ref, "relaxed")
            
        # Navigation buttons
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            if st.session_state.current_question > 0:
                if st.button("Previous Question"):
                    self.prev_question()
                    
        with col2:
            if st.session_state.current_question < len(st.session_state.question_flow) - 1:
                if st.button("Next Question"):
                    self.record_time_spent()
                    st.session_state.current_question += 1
                    st.session_state.relaxed_start_times[self.get_current_question_index()] = time.time()
                    st.session_state.last_question_change = time.time()
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
        
        # Process main questions
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
            
            # Add conditional questions if they were shown
            if "conditional" in question and question["conditional"].get("strict", False):
                cond_key = f"conditional_{i}"
                if st.session_state.active_conditional_questions.get(cond_key, False):
                    cond_question = question["conditional"]["follow_up"]
                    cond_timer = st.session_state.timer_answers.get(cond_key)
                    cond_relaxed = st.session_state.relaxed_answers.get(cond_key)
                    
                    formatted_cond_timer = self.format_answer_for_display(cond_timer, cond_question["type"])
                    formatted_cond_relaxed = self.format_answer_for_display(cond_relaxed, cond_question["type"])
                    
                    if cond_timer != cond_relaxed:
                        answer_changes += 1
                        
                    results.append({
                        "Question": f"Follow-up: {cond_question['question']}",
                        "Type": cond_question["type"].replace("_", " ").title(),
                        "Timer Answer": formatted_cond_timer,
                        "Relaxed Answer": formatted_cond_relaxed,
                        "Changed": "Yes" if cond_timer != cond_relaxed else "No",
                        "Time Spent (Relaxed)": f"{st.session_state.relaxed_time_spent.get(cond_key, 0):.1f} seconds"
                    })
        
        df = pd.DataFrame(results)
        st.dataframe(df)
        
        # Show summary statistics
        st.subheader("Summary")
        st.metric("Total Questions Answered", len([r for r in results if r["Timer Answer"] != "Not answered"]))
        st.metric("Answers Changed in Relaxed Mode", answer_changes)
        
        # Calculate total time spent
        total_time = sum([t for t in st.session_state.relaxed_time_spent.values() if isinstance(t, (int, float))])
        st.metric("Total Time Spent in Relaxed Mode", f"{total_time:.1f} seconds")
        
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
                current_q_ref = self.get_current_question_index()
                if current_q_ref in st.session_state.relaxed_start_times:
                    time_spent = time.time() - st.session_state.relaxed_start_times[current_q_ref]
                    st.write(f"Time spent on current question: {time_spent:.1f} seconds")
                    
                    # Show time since last question change
                    time_since_change = time.time() - st.session_state.last_question_change
                    st.write(f"Time on this question: {time_since_change:.1f} seconds")
                    
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