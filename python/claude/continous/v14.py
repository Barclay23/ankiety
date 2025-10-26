import streamlit as st
import time
import pandas as pd
import json
from datetime import datetime
from typing import Dict, List, Union, Optional, Any

# Set page config
st.set_page_config(page_title="Enhanced Survey Application", layout="wide")

# Apply custom CSS for blue background and white text
st.markdown("""
<style>
    /* Main background and text color */
    .stApp {
        background-color: #1E3A8A;
        color: white;
    }
    
    /* Style for headers */
    h1, h2, h3, h4, h5, h6 {
        color: white !important;
    }
    
    /* Style for standard text */
    p, div, span, label {
        color: white !important;
    }
    
    /* Style for warning, info and other message containers */
    .stAlert > div {
        color: white !important;
        background-color: rgba(255, 255, 255, 0.1) !important;
        border-color: rgba(255, 255, 255, 0.2) !important;
    }
    
    /* Style for radio buttons text */
    .stRadio label {
        color: white !important;
    }
    
    /* Style for button text */
    .stButton button {
        color: white !important;
        background-color: #3B82F6 !important;
        border-color: #60A5FA !important;
    }
    
    /* Style for button hover */
    .stButton button:hover {
        background-color: #2563EB !important;
    }
    
    /* Tables styling */
    .dataframe {
        color: white !important;
    }
    
    .dataframe th {
        background-color: #2563EB !important;
        color: white !important;
    }
    
    .dataframe td {
        background-color: #3B82F6 !important;
        color: white !important;
    }
    
    /* Progress bar styling */
    .stProgress > div > div {
        background-color: #60A5FA !important;
    }
    
    /* Fix for markdown text */
    .css-1offfwp p {
        color: white !important;
    }
    
    /* Radio buttons styling */
    .stRadio > div[role="radiogroup"] > label > div {
        background-color: rgba(255, 255, 255, 0.1) !important;
        border-color: rgba(255, 255, 255, 0.2) !important;
    }
    
    /* Text inputs styling */
    .stTextInput input, .stTextArea textarea {
        background-color: rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border-color: rgba(255, 255, 255, 0.2) !important;
    }
    
    /* Checkbox styling */
    .stCheckbox label {
        color: white !important;
    }
    
    /* Selectbox styling */
    .stSelectbox > div > div {
        background-color: rgba(255, 255, 255, 0.1) !important;
        color: white !important;
    }
    
    /* Slider styling */
    .stSlider label {
        color: white !important;
    }
    
    /* Make sure tooltips and hover states are visible */
    [data-baseweb="tooltip"] {
        background-color: #2563EB !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# Define question types
class QuestionType:
    MULTIPLE_CHOICE = "multiple_choice"
    OPEN_ENDED = "open_ended"
    MULTIPLE_SELECT = "multiple_select"
    RATING = "rating"
    DROPDOWN = "dropdown"
    # New question types
    SLIDER_RANGE = "slider_range"
    FILE_UPLOAD = "file_upload"
    NUMBER_INPUT = "number_input"
    DATE_INPUT = "date_input"
    LIKERT_SCALE = "likert_scale"

# Initialize session state variables
def init_session_state():
    """Initialize all session state variables with proper typing"""
    if 'mode' not in st.session_state:
        st.session_state.mode = "timer_mode"  # Start with timer mode
    if 'current_question' not in st.session_state:
        st.session_state.current_question = 0
    if 'timer_answers' not in st.session_state:
        st.session_state.timer_answers = {}
    if 'relaxed_answers' not in st.session_state:
        st.session_state.relaxed_answers = {}
    if 'timer_mode_completed' not in st.session_state:
        st.session_state.timer_mode_completed = False
    if 'question_start_time' not in st.session_state:
        st.session_state.question_start_time = None
    if 'relaxed_time_spent' not in st.session_state:
        st.session_state.relaxed_time_spent = {}
    if 'current_timer_start_time' not in st.session_state:
        st.session_state.current_timer_start_time = time.time()
    if 'timer_current_selection' not in st.session_state:
        st.session_state.timer_current_selection = None
    if 'last_update' not in st.session_state:
        st.session_state.last_update = time.time()
    if 'reset_timer' not in st.session_state:
        st.session_state.reset_timer = True
    # For multiple select questions
    if 'timer_current_multi_selection' not in st.session_state:
        st.session_state.timer_current_multi_selection = []
    # For open-ended questions
    if 'timer_current_text_input' not in st.session_state:
        st.session_state.timer_current_text_input = ""
    # For rating questions
    if 'timer_current_rating' not in st.session_state:
        st.session_state.timer_current_rating = None
    if 'timer_current_slider_range' not in st.session_state:
        st.session_state.timer_current_slider_range = None
    if 'timer_current_number_input' not in st.session_state:
        st.session_state.timer_current_number_input = None
    if 'timer_current_date' not in st.session_state:
        st.session_state.timer_current_date = None
    if 'timer_current_likert' not in st.session_state:
        st.session_state.timer_current_likert = None

# Enhanced questions list with multiple types
questions = [
    {
        "type": QuestionType.MULTIPLE_CHOICE,
        "question": "What is the capital of France?",
        "options": ["Berlin", "Madrid", "Paris", "Rome"],
        "time_limit": 10  # seconds
    },
    {
        "type": QuestionType.OPEN_ENDED,
        "question": "Describe your favorite vacation destination and why you enjoy it.",
        "time_limit": 30  # seconds
    },
    {
        "type": QuestionType.MULTIPLE_SELECT,
        "question": "Which of the following programming languages have you used? (Select all that apply)",
        "options": ["Python", "JavaScript", "Java", "C++", "Ruby", "Go"],
        "time_limit": 15  # seconds
    },
    {
        "type": QuestionType.RATING,
        "question": "On a scale of 1-10, how would you rate your experience with Streamlit?",
        "min": 1,
        "max": 10,
        "time_limit": 8  # seconds
    },
    {
        "type": QuestionType.MULTIPLE_CHOICE,
        "question": "Which planet is known as the Red Planet?",
        "options": ["Earth", "Mars", "Jupiter", "Venus"],
        "time_limit": 8  # seconds
    },
    {
        "type": QuestionType.DROPDOWN,
        "question": "Which of the following is your favorite movie genre?",
        "options": ["Action", "Comedy", "Drama", "Science Fiction", "Horror", "Romance", "Documentary"],
        "time_limit": 12  # seconds
    },
    {
        "type": QuestionType.OPEN_ENDED,
        "question": "What improvements would you suggest for this survey application?",
        "time_limit": 25  # seconds
    },
    {
        "type": QuestionType.SLIDER_RANGE,
        "question": "What is your acceptable price range for a new smartphone?",
        "min": 100,
        "max": 2000,
        "step": 50,
        "time_limit": 15  # seconds
    },
    {
        "type": QuestionType.NUMBER_INPUT,
        "question": "How many hours do you spend on social media per day?",
        "min": 0,
        "max": 24,
        "step": 0.5,
        "time_limit": 10  # seconds
    },
    {
        "type": QuestionType.DATE_INPUT,
        "question": "When did you last upgrade your computer/laptop?",
        "time_limit": 15  # seconds
    },
    {
        "type": QuestionType.LIKERT_SCALE,
        "question": "This survey was easy to complete.",
        "options": ["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"],
        "time_limit": 12  # seconds
    },
    {
        "type": QuestionType.MULTIPLE_CHOICE,
        "question": "Which emerging technology do you think will have the biggest impact in the next 5 years?",
        "options": ["Artificial Intelligence", "Quantum Computing", "Biotechnology", "Renewable Energy", "Space Technology"],
        "time_limit": 15  # seconds
    },
    {
        "type": QuestionType.OPEN_ENDED,
        "question": "How has technology changed your daily life in the past year?",
        "time_limit": 30  # seconds
    },
]

def switch_to_relaxed_mode():
    """Switch from timer mode to relaxed mode."""
    st.session_state.mode = "relaxed_mode"
    st.session_state.current_question = 0
    st.session_state.timer_mode_completed = True
    st.session_state.question_start_time = datetime.now()

def next_question():
    """Move to the next question or switch modes if at the end."""
    if st.session_state.current_question < len(questions) - 1:
        st.session_state.current_question += 1
        if st.session_state.mode == "relaxed_mode":
            st.session_state.question_start_time = datetime.now()
        elif st.session_state.mode == "timer_mode":
            # Mark timer for reset
            st.session_state.reset_timer = True
            # Reset current selections
            st.session_state.timer_current_selection = None
            st.session_state.timer_current_multi_selection = []
            st.session_state.timer_current_text_input = ""
            st.session_state.timer_current_rating = None
    else:
        if st.session_state.mode == "timer_mode":
            switch_to_relaxed_mode()
        else:
            st.session_state.mode = "completed"

def previous_question():
    """Move to the previous question (only in relaxed mode)."""
    if st.session_state.current_question > 0:
        st.session_state.current_question -= 1
        if st.session_state.mode == "relaxed_mode":
            st.session_state.question_start_time = datetime.now()

def save_relaxed_answer(idx: int, selected_option: Any):
    """Save the answer for relaxed mode and update time tracking."""
    # Save the current answer and update time spent
    st.session_state.relaxed_answers[idx] = selected_option
    if st.session_state.question_start_time is not None:
        time_spent = (datetime.now() - st.session_state.question_start_time).total_seconds()
        # If there's already time recorded for this question, add to it
        current_time = st.session_state.relaxed_time_spent.get(idx, 0)
        st.session_state.relaxed_time_spent[idx] = current_time + time_spent
        st.session_state.question_start_time = datetime.now()

def on_answer_change(idx: int, key: str):
    """Called when any input value changes in relaxed mode."""
    if key in st.session_state:
        selected = st.session_state[key]
        save_relaxed_answer(idx, selected)

def update_timer_selection(question_type: str):
    """Update the current selection without rerunning the page in timer mode."""
    current_idx = st.session_state.current_question
    
    if question_type == QuestionType.MULTIPLE_CHOICE or question_type == QuestionType.DROPDOWN:
        key = f"timer_{question_type}_{current_idx}"
        if key in st.session_state:
            st.session_state.timer_current_selection = st.session_state[key]
    
    elif question_type == QuestionType.MULTIPLE_SELECT:
        key = f"timer_{question_type}_{current_idx}"
        if key in st.session_state:
            st.session_state.timer_current_multi_selection = st.session_state[key]
    
    elif question_type == QuestionType.OPEN_ENDED:
        key = f"timer_{question_type}_{current_idx}"
        if key in st.session_state:
            st.session_state.timer_current_text_input = st.session_state[key]
    
    elif question_type == QuestionType.RATING:
        key = f"timer_{question_type}_{current_idx}"
        if key in st.session_state:
            st.session_state.timer_current_rating = st.session_state[key]
    elif question_type == QuestionType.SLIDER_RANGE:
        key = f"timer_{question_type}_{current_idx}"
        if key in st.session_state:
            st.session_state.timer_current_slider_range = st.session_state[key]
    
    elif question_type == QuestionType.NUMBER_INPUT:
        key = f"timer_{question_type}_{current_idx}"
        if key in st.session_state:
            st.session_state.timer_current_number_input = st.session_state[key]
    
    elif question_type == QuestionType.DATE_INPUT:
        key = f"timer_{question_type}_{current_idx}"
        if key in st.session_state:
            st.session_state.timer_current_date = st.session_state[key]
    
    elif question_type == QuestionType.LIKERT_SCALE:
        key = f"timer_{question_type}_{current_idx}"
        if key in st.session_state:
            st.session_state.timer_current_likert = st.session_state[key]

def format_answer_for_display(question_type: str, answer: Any) -> str:
    """Format different answer types for display in results table"""
    if answer is None or answer == "":
        return "No answer"
        
    if question_type == QuestionType.MULTIPLE_SELECT:
        if isinstance(answer, list) and len(answer) > 0:
            return ", ".join(answer)
        return "None selected"
    
    if question_type == QuestionType.SLIDER_RANGE:
        if isinstance(answer, (list, tuple)) and len(answer) == 2:
            return f"${answer[0]} - ${answer[1]}"
        return "No range selected"
    
    if question_type == QuestionType.DATE_INPUT:
        if isinstance(answer, (datetime, str)):
            return str(answer)
        return "No date selected"
    
    return str(answer)

def display_results():
    """Display the final results from both survey modes."""
    st.title("Survey Results")
    
    # Create dataframes for displaying results
    timer_results = []
    relaxed_results = []
    
    for i, q in enumerate(questions):
        question_type = q["type"]
        question_text = q["question"]
        
        # Process timer mode answers
        timer_answer = st.session_state.timer_answers.get(i, "No answer")
        timer_results.append({
            "Question": f"Q{i+1}: {question_text[:30]}{'...' if len(question_text) > 30 else ''}",
            "Question Type": question_type.replace('_', ' ').title(),
            "Your Answer": format_answer_for_display(question_type, timer_answer)
        })
        
        # Process relaxed mode answers
        relaxed_answer = st.session_state.relaxed_answers.get(i, "No answer")
        time_spent = f"{st.session_state.relaxed_time_spent.get(i, 0):.2f}s"
        relaxed_results.append({
            "Question": f"Q{i+1}: {question_text[:30]}{'...' if len(question_text) > 30 else ''}",
            "Question Type": question_type.replace('_', ' ').title(),
            "Your Answer": format_answer_for_display(question_type, relaxed_answer),
            "Time Spent": time_spent
        })
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Timer Mode Answers")
        timer_df = pd.DataFrame(timer_results)
        st.table(timer_df)
    
    with col2:
        st.subheader("Relaxed Mode Answers")
        relaxed_df = pd.DataFrame(relaxed_results)
        st.table(relaxed_df)
    
    # Display differences between the two modes
    st.subheader("Comparison of Answers Between Modes")
    
    differences = []
    for i, q in enumerate(questions):
        timer_answer = st.session_state.timer_answers.get(i, "No answer")
        relaxed_answer = st.session_state.relaxed_answers.get(i, "No answer")
        
        # Handle different question types for comparison
        is_different = False
        if q["type"] == QuestionType.MULTIPLE_SELECT:
            if isinstance(timer_answer, list) and isinstance(relaxed_answer, list):
                is_different = set(timer_answer) != set(relaxed_answer)
            else:
                is_different = timer_answer != relaxed_answer
        else:
            is_different = timer_answer != relaxed_answer
        
        if is_different:
            differences.append({
                "Question": f"Q{i+1}: {q['question'][:30]}{'...' if len(q['question']) > 30 else ''}",
                "Timer Mode Answer": format_answer_for_display(q["type"], timer_answer),
                "Relaxed Mode Answer": format_answer_for_display(q["type"], relaxed_answer)
            })
    
    if differences:
        st.table(pd.DataFrame(differences))
    else:
        st.info("Your answers were the same in both modes!")
    
    # Export results option
    st.subheader("Export Results")
    
    if st.button("Export as JSON", key="export_button"):
        export_data = {
            "timer_mode": {
                f"question_{i+1}": {
                    "question": q["question"],
                    "type": q["type"],
                    "answer": st.session_state.timer_answers.get(i, "No answer")
                } for i, q in enumerate(questions)
            },
            "relaxed_mode": {
                f"question_{i+1}": {
                    "question": q["question"],
                    "type": q["type"],
                    "answer": st.session_state.relaxed_answers.get(i, "No answer"),
                    "time_spent": f"{st.session_state.relaxed_time_spent.get(i, 0):.2f}s"
                } for i, q in enumerate(questions)
            }
        }
        
        # Convert to JSON and offer download
        json_data = json.dumps(export_data, indent=4)
        st.download_button(
            label="Download JSON",
            data=json_data,
            file_name="survey_results.json",
            mime="application/json"
        )
    
    # Add a restart button
    if st.button("Start New Survey", key="restart_button"):
        # Reset all session state variables
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

def get_timer_progress():
    """Calculate the current timer progress value (0-1)."""
    if st.session_state.mode != "timer_mode":
        return 0
    
    current_idx = st.session_state.current_question
    time_limit = questions[current_idx]["time_limit"]
    elapsed_time = time.time() - st.session_state.current_timer_start_time
    remaining_time = max(0, time_limit - elapsed_time)
    
    # Return value between 0 and 1 representing remaining time
    return remaining_time / time_limit

def check_timer_expiration():
    """Check if the timer for current question has expired."""
    if st.session_state.mode != "timer_mode":
        return False
    
    current_idx = st.session_state.current_question
    time_limit = questions[current_idx]["time_limit"]
    elapsed_time = time.time() - st.session_state.current_timer_start_time
    
    # If time's up, save answer and move to next question
    if elapsed_time >= time_limit:
        # Save the answer based on question type
        question_type = questions[current_idx]["type"]
        
        if question_type == QuestionType.MULTIPLE_CHOICE or question_type == QuestionType.DROPDOWN:
            st.session_state.timer_answers[current_idx] = (
                st.session_state.timer_current_selection if st.session_state.timer_current_selection else "No answer"
            )
        elif question_type == QuestionType.MULTIPLE_SELECT:
            st.session_state.timer_answers[current_idx] = (
                st.session_state.timer_current_multi_selection if st.session_state.timer_current_multi_selection else []
            )
        elif question_type == QuestionType.OPEN_ENDED:
            st.session_state.timer_answers[current_idx] = (
                st.session_state.timer_current_text_input if st.session_state.timer_current_text_input else "No answer"
            )
        elif question_type == QuestionType.RATING:
            st.session_state.timer_answers[current_idx] = (
                st.session_state.timer_current_rating if st.session_state.timer_current_rating is not None else "No answer"
            )
        
        elif question_type == QuestionType.SLIDER_RANGE:
            st.session_state.timer_answers[current_idx] = (
                st.session_state.timer_current_slider_range if st.session_state.timer_current_slider_range is not None else "No answer"
            )
        elif question_type == QuestionType.NUMBER_INPUT:
            st.session_state.timer_answers[current_idx] = (
                st.session_state.timer_current_number_input if st.session_state.timer_current_number_input is not None else "No answer"
            )
        elif question_type == QuestionType.DATE_INPUT:
            st.session_state.timer_answers[current_idx] = (
                st.session_state.timer_current_date if st.session_state.timer_current_date is not None else "No answer"
            )
        elif question_type == QuestionType.LIKERT_SCALE:
            st.session_state.timer_answers[current_idx] = (
                st.session_state.timer_current_likert if st.session_state.timer_current_likert is not None else "No answer"
            )
            
        # Move to next question
        next_question()
        return True
    
    return False

def render_timer_question(current_idx: int, question: Dict[str, Any]):
    """Render the appropriate input for a timer mode question based on its type."""
    question_type = question["type"]
    
    if question_type == QuestionType.MULTIPLE_CHOICE:
        # Find index of current selection if any
        option_index = None
        if st.session_state.timer_current_selection in question["options"]:
            option_index = question["options"].index(st.session_state.timer_current_selection)
        
        # Radio buttons for multiple choice
        st.radio(
            "Select your answer:",
            options=question["options"],
            key=f"timer_{question_type}_{current_idx}",
            index=option_index,
            on_change=lambda: update_timer_selection(question_type)
        )
    
    elif question_type == QuestionType.OPEN_ENDED:
        # Text area for open-ended questions
        st.text_area(
            "Your answer:",
            value=st.session_state.timer_current_text_input,
            key=f"timer_{question_type}_{current_idx}",
            on_change=lambda: update_timer_selection(question_type),
            height=150
        )
    
    elif question_type == QuestionType.MULTIPLE_SELECT:
        # Checkboxes for multiple select
        st.multiselect(
            "Select all that apply:",
            options=question["options"],
            default=st.session_state.timer_current_multi_selection,
            key=f"timer_{question_type}_{current_idx}",
            on_change=lambda: update_timer_selection(question_type)
        )
    
    elif question_type == QuestionType.RATING:
        # Slider for rating questions
        st.slider(
            "Your rating:",
            min_value=question["min"],
            max_value=question["max"],
            value=st.session_state.timer_current_rating if st.session_state.timer_current_rating is not None else question["min"],
            key=f"timer_{question_type}_{current_idx}",
            on_change=lambda: update_timer_selection(question_type)
        )
    
    elif question_type == QuestionType.DROPDOWN:
        # Dropdown for selection
        option_index = 0
        if st.session_state.timer_current_selection in question["options"]:
            option_index = question["options"].index(st.session_state.timer_current_selection)
        
        st.selectbox(
            "Select one option:",
            options=question["options"],
            index=option_index,
            key=f"timer_{question_type}_{current_idx}",
            on_change=lambda: update_timer_selection(question_type)
        )
    
    elif question_type == QuestionType.SLIDER_RANGE:
        # Range slider for price range
        default_value = [question["min"], question["max"]] if st.session_state.timer_current_slider_range is None else st.session_state.timer_current_slider_range
        st.slider(
            "Select price range:",
            min_value=question["min"],
            max_value=question["max"],
            value=default_value,
            step=question.get("step", 1),
            key=f"timer_{question_type}_{current_idx}",
            on_change=lambda: update_timer_selection(question_type),
            format="$%d"
        )
    
    elif question_type == QuestionType.NUMBER_INPUT:
        # Number input for numerical values
        default_value = question["min"] if st.session_state.timer_current_number_input is None else st.session_state.timer_current_number_input
        st.number_input(
            "Enter value:",
            min_value=question["min"],
            max_value=question["max"],
            value=default_value,
            step=question.get("step", 1),
            key=f"timer_{question_type}_{current_idx}",
            on_change=lambda: update_timer_selection(question_type)
        )
    
    elif question_type == QuestionType.DATE_INPUT:
        # Date picker
        today = datetime.now().date()
        default_value = today if st.session_state.timer_current_date is None else st.session_state.timer_current_date
        st.date_input(
            "Select date:",
            value=default_value,
            key=f"timer_{question_type}_{current_idx}",
            on_change=lambda: update_timer_selection(question_type)
        )
    
    elif question_type == QuestionType.LIKERT_SCALE:
        # Likert scale as radio buttons with horizontal layout
        option_index = None
        if st.session_state.timer_current_likert in question["options"]:
            option_index = question["options"].index(st.session_state.timer_current_likert)
        
        st.write("Please rate your agreement:")
        cols = st.columns(len(question["options"]))
        
        for i, option in enumerate(question["options"]):
            with cols[i]:
                st.write(option)
                selected = st.radio(
                    "",
                    [""],
                    key=f"timer_likert_option_{current_idx}_{i}",
                    label_visibility="collapsed",
                    index=0 if option_index == i else None
                )
                if selected:
                    st.session_state[f"timer_{question_type}_{current_idx}"] = option
                    update_timer_selection(question_type)

def render_relaxed_question(current_idx: int, question: Dict[str, Any]):
    """Render the appropriate input for a relaxed mode question based on its type."""
    question_type = question["type"]
    
    # Get default values from either relaxed or timer mode answers
    default_value = st.session_state.relaxed_answers.get(current_idx, None)
    if default_value is None and current_idx in st.session_state.timer_answers:
        default_value = st.session_state.timer_answers[current_idx]
    
    if question_type == QuestionType.MULTIPLE_CHOICE:
        # Set default index if available
        option_index = None
        if default_value in question["options"]:
            option_index = question["options"].index(default_value)
        
        # Radio buttons for multiple choice
        st.radio(
            "Select your answer:",
            options=question["options"],
            key=f"relaxed_{question_type}_{current_idx}",
            index=option_index,
            on_change=lambda: on_answer_change(current_idx, f"relaxed_{question_type}_{current_idx}")
        )
    
    elif question_type == QuestionType.OPEN_ENDED:
        # Text area for open-ended questions
        st.text_area(
            "Your answer:",
            value="" if default_value == "No answer" else default_value,
            key=f"relaxed_{question_type}_{current_idx}",
            on_change=lambda: on_answer_change(current_idx, f"relaxed_{question_type}_{current_idx}"),
            height=150
        )
    
    elif question_type == QuestionType.MULTIPLE_SELECT:
        # Handle default value for multiselect
        if not isinstance(default_value, list):
            default_value = []
        
        # Checkboxes for multiple select
        st.multiselect(
            "Select all that apply:",
            options=question["options"],
            default=default_value,
            key=f"relaxed_{question_type}_{current_idx}",
            on_change=lambda: on_answer_change(current_idx, f"relaxed_{question_type}_{current_idx}")
        )
    
    elif question_type == QuestionType.RATING:
        # Default to min value if no rating was selected
        if default_value == "No answer" or default_value is None:
            default_value = question["min"]
        
        # Slider for rating questions
        st.slider(
            "Your rating:",
            min_value=question["min"],
            max_value=question["max"],
            value=default_value,
            key=f"relaxed_{question_type}_{current_idx}",
            on_change=lambda: on_answer_change(current_idx, f"relaxed_{question_type}_{current_idx}")
        )
    
    elif question_type == QuestionType.DROPDOWN:
        # Default index
        option_index = 0
        if default_value in question["options"]:
            option_index = question["options"].index(default_value)
        
        # Dropdown for selection
        st.selectbox(
            "Select one option:",
            options=question["options"],
            index=option_index,
            key=f"relaxed_{question_type}_{current_idx}",
            on_change=lambda: on_answer_change(current_idx, f"relaxed_{question_type}_{current_idx}")
        )
    
    elif question_type == QuestionType.SLIDER_RANGE:
        # Default range values
        if not isinstance(default_value, (list, tuple)) or len(default_value) != 2:
            default_value = [question["min"], question["max"]]
        
        # Range slider for price range
        step = question.get("step", 1)
        st.slider(
            "Select price range:",
            min_value=question["min"],
            max_value=question["max"],
            value=default_value,
            step=step,
            key=f"relaxed_{question_type}_{current_idx}",
            on_change=lambda: on_answer_change(current_idx, f"relaxed_{question_type}_{current_idx}"),
            format="$%d"
        )
    
    elif question_type == QuestionType.NUMBER_INPUT:
        # Default number value
        if default_value == "No answer" or default_value is None:
            default_value = question["min"]
        
        # Number input for numerical values - ensure type consistency
        step = question.get("step", 1)
        
        # Convert all values to float if step is float, or int if step is int
        if isinstance(step, float):
            min_val = float(question["min"])
            max_val = float(question["max"])
            default_val = float(default_value)
        else:
            min_val = int(question["min"])
            max_val = int(question["max"])
            default_val = int(default_value)
            step = int(step)
        
        st.number_input(
            "Enter value:",
            min_value=min_val,
            max_value=max_val,
            value=default_val,
            step=step,
            key=f"relaxed_{question_type}_{current_idx}",
            on_change=lambda: on_answer_change(current_idx, f"relaxed_{question_type}_{current_idx}")
        )
    
    elif question_type == QuestionType.DATE_INPUT:
        # Default date
        today = datetime.now().date()
        if default_value == "No answer" or default_value is None:
            default_value = today
        elif isinstance(default_value, str):
            try:
                default_value = datetime.strptime(default_value, "%Y-%m-%d").date()
            except:
                default_value = today
        
        # Date picker
        st.date_input(
            "Select date:",
            value=default_value,
            key=f"relaxed_{question_type}_{current_idx}",
            on_change=lambda: on_answer_change(current_idx, f"relaxed_{question_type}_{current_idx}")
        )
    
    elif question_type == QuestionType.LIKERT_SCALE:
        # Determine selected option index
        option_index = None
        if default_value in question["options"]:
            option_index = question["options"].index(default_value)
        
        # Likert scale as horizontal radio buttons
        st.write("Please rate your agreement:")
        cols = st.columns(len(question["options"]))
        
        for i, option in enumerate(question["options"]):
            with cols[i]:
                st.write(option)
                selected = st.radio(
                    "",
                    [""],
                    key=f"relaxed_likert_option_{current_idx}_{i}",
                    label_visibility="collapsed",
                    index=0 if option_index == i else None
                )
                if selected:
                    st.session_state[f"relaxed_{question_type}_{current_idx}"] = option
                    on_answer_change(current_idx, f"relaxed_{question_type}_{current_idx}")

def save_current_timer_answer(current_idx: int):
    """Save the current answer in timer mode based on the question type."""
    question_type = questions[current_idx]["type"]
    
    if question_type == QuestionType.MULTIPLE_CHOICE or question_type == QuestionType.DROPDOWN:
        st.session_state.timer_answers[current_idx] = (
            st.session_state.timer_current_selection if st.session_state.timer_current_selection else "No answer"
        )
    elif question_type == QuestionType.MULTIPLE_SELECT:
        st.session_state.timer_answers[current_idx] = (
            st.session_state.timer_current_multi_selection if st.session_state.timer_current_multi_selection else []
        )
    elif question_type == QuestionType.OPEN_ENDED:
        st.session_state.timer_answers[current_idx] = (
            st.session_state.timer_current_text_input if st.session_state.timer_current_text_input else "No answer"
        )
    elif question_type == QuestionType.RATING:
        st.session_state.timer_answers[current_idx] = (
            st.session_state.timer_current_rating if st.session_state.timer_current_rating is not None else "No answer"
        )

    elif question_type == QuestionType.SLIDER_RANGE:
        st.session_state.timer_answers[current_idx] = (
            st.session_state.timer_current_slider_range if st.session_state.timer_current_slider_range is not None else "No answer"
        )
    elif question_type == QuestionType.NUMBER_INPUT:
        st.session_state.timer_answers[current_idx] = (
            st.session_state.timer_current_number_input if st.session_state.timer_current_number_input is not None else "No answer"
        )
    elif question_type == QuestionType.DATE_INPUT:
        st.session_state.timer_answers[current_idx] = (
            st.session_state.timer_current_date if st.session_state.timer_current_date is not None else "No answer"
        )
    elif question_type == QuestionType.LIKERT_SCALE:
        st.session_state.timer_answers[current_idx] = (
            st.session_state.timer_current_likert if st.session_state.timer_current_likert is not None else "No answer"
        )

def main():
    """Main application function."""
    # Initialize session state
    init_session_state()
    
    # Reset timer when necessary (new question)
    if st.session_state.mode == "timer_mode" and st.session_state.reset_timer:
        st.session_state.current_timer_start_time = time.time()
        st.session_state.reset_timer = False
    
    # Display the appropriate content based on the current mode
    if st.session_state.mode == "timer_mode":
        display_timer_mode()
    elif st.session_state.mode == "relaxed_mode":
        display_relaxed_mode()
    elif st.session_state.mode == "completed":
        display_results()
    else:
        st.error("Unknown application mode")

def display_timer_mode():
    """Display the timer mode interface."""
    current_idx = st.session_state.current_question
    
    # Display progress information
    st.markdown(f"### Timer Mode: Question {current_idx + 1} of {len(questions)}")
    
    # Display the timer progress bar
    remaining_time = questions[current_idx]["time_limit"] - (time.time() - st.session_state.current_timer_start_time)
    progress_value = get_timer_progress()
    
    # Display timer bar and remaining time
    col1, col2 = st.columns([4, 1])
    with col1:
        st.progress(progress_value)
    with col2:
        st.write(f"{max(0, int(remaining_time))}s left")
    
    # Display the current question
    st.markdown(f"## {questions[current_idx]['question']}")
    
    # Render the appropriate input for this question type
    render_timer_question(current_idx, questions[current_idx])
    
    # Add a submit button
    if st.button("Submit Answer", key="timer_submit"):
        save_current_timer_answer(current_idx)
        next_question()
        st.rerun()
    
    # Check if timer expired and update UI if necessary
    if check_timer_expiration():
        st.rerun()

def display_relaxed_mode():
    """Display the relaxed mode interface."""
    current_idx = st.session_state.current_question
    
    # Display progress information
    st.markdown(f"### Relaxed Mode: Question {current_idx + 1} of {len(questions)}")
    st.markdown("Take your time to answer each question.")
    
    # Display the current question
    st.markdown(f"## {questions[current_idx]['question']}")
    
    # Render the appropriate input for this question type
    render_relaxed_question(current_idx, questions[current_idx])
    
    # Navigation buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if current_idx > 0:
            if st.button("Previous", key="relaxed_prev"):
                previous_question()
                st.rerun()
    
    with col2:
        next_button_text = "Next" if current_idx < len(questions) - 1 else "Finish"
        if st.button(next_button_text, key="relaxed_next"):
            # Save the current answer before moving on
            question_type = questions[current_idx]["type"]
            key = f"relaxed_{question_type}_{current_idx}"
            if key in st.session_state:
                save_relaxed_answer(current_idx, st.session_state[key])
            next_question()
            st.rerun()

# Add a call to the main function at the end of the script
if __name__ == "__main__":
    main()