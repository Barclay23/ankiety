import streamlit as st
import time
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pandas as pd

# Configuration
SURVEY_QUESTIONS = [
    "How satisfied are you with our product?",
    "How likely are you to recommend us to a friend?",
    "How would you rate our customer service?",
    "What features would you like to see in future updates?",
    "Any additional comments or feedback?"
]
QUESTION_TYPES = ["scale 1-5", "scale 1-10", "scale 1-5", "text", "text"]
EMAIL_RECEIVER = "survey.results@example.com"  # Replace with your email
EMAIL_SENDER = "survey.app@example.com"  # Replace with your sender email
EMAIL_PASSWORD = "your_email_password"  # Replace with your email password or use app-specific password

# Initialize session state
if 'answers' not in st.session_state:
    st.session_state.answers = {i: None for i in range(len(SURVEY_QUESTIONS))}
if 'current_question' not in st.session_state:
    st.session_state.current_question = 0
if 'start_time' not in st.session_state:
    st.session_state.start_time = time.time()
if 'question_times' not in st.session_state:
    st.session_state.question_times = {i: 0 for i in range(len(SURVEY_QUESTIONS))}
if 'mode' not in st.session_state:
    st.session_state.mode = None
if 'timer_start' not in st.session_state:
    st.session_state.timer_start = None
if 'time_per_question' not in st.session_state:
    st.session_state.time_per_question = 30  # Default 30 seconds per question in timer mode

def send_email(answers_data):
    """Send survey results via email"""
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = EMAIL_SENDER
        msg['To'] = EMAIL_RECEIVER
        msg['Subject'] = f"Survey Results - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        # Create HTML content
        html = f"""
        <h1>Survey Results</h1>
        <p>Submitted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <table border="1">
            <tr>
                <th>Question</th>
                <th>Answer</th>
                <th>Time Spent (s)</th>
            </tr>
        """
        
        for i, question in enumerate(SURVEY_QUESTIONS):
            html += f"""
            <tr>
                <td>{question}</td>
                <td>{answers_data[i]['answer']}</td>
                <td>{answers_data[i]['time_spent']:.1f}</td>
            </tr>
            """
        
        html += "</table>"
        
        msg.attach(MIMEText(html, 'html'))
        
        # Send email
        with smtplib.SMTP_SSL('smtp.example.com', 465) as server:  # Replace with your SMTP server
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)
        
        return True
    except Exception as e:
        st.error(f"Failed to send email: {e}")
        return False

def display_question_timer_mode(q_index):
    """Display question in timer mode"""
    st.progress((q_index + 1) / len(SURVEY_QUESTIONS))
    
    # Timer display
    time_left = max(0, st.session_state.time_per_question - (time.time() - st.session_state.timer_start))
    timer_placeholder = st.empty()
    
    # Visual warning when time is running out
    if time_left < 10:
        timer_placeholder.warning(f"Time left: {int(time_left)} seconds")
    else:
        timer_placeholder.info(f"Time left: {int(time_left)} seconds")
    
    # Question display
    st.subheader(f"Question {q_index + 1}/{len(SURVEY_QUESTIONS)}")
    st.markdown(f"**{SURVEY_QUESTIONS[q_index]}**")
    
    # Answer input based on question type
    if QUESTION_TYPES[q_index].startswith("scale"):
        scale_range = int(QUESTION_TYPES[q_index].split("-")[-1])
        answer = st.radio("Your answer:", options=list(range(1, scale_range + 1)), horizontal=True)
    else:
        answer = st.text_area("Your answer:", height=100)
    
    # Auto-advance when time is up
    if time.time() - st.session_state.timer_start > st.session_state.time_per_question:
        st.session_state.answers[q_index] = answer
        st.session_state.current_question += 1
        if st.session_state.current_question < len(SURVEY_QUESTIONS):
            st.session_state.timer_start = time.time()
            st.rerun()
    
    # Manual submit button
    if st.button("Submit Answer"):
        st.session_state.answers[q_index] = answer
        st.session_state.current_question += 1
        if st.session_state.current_question < len(SURVEY_QUESTIONS):
            st.session_state.timer_start = time.time()
            st.rerun()

def display_question_relaxed_mode(q_index):
    """Display question in relaxed mode"""
    st.progress((q_index + 1) / len(SURVEY_QUESTIONS))
    
    # Question display
    st.subheader(f"Question {q_index + 1}/{len(SURVEY_QUESTIONS)}")
    st.markdown(f"**{SURVEY_QUESTIONS[q_index]}**")
    
    # Time tracking
    if 'last_question_time' not in st.session_state:
        st.session_state.last_question_time = time.time()
    
    # Answer input based on question type
    if QUESTION_TYPES[q_index].startswith("scale"):
        scale_range = int(QUESTION_TYPES[q_index].split("-")[-1])
        answer = st.radio("Your answer:", 
                         options=list(range(1, scale_range + 1)), 
                         horizontal=True,
                         index=(st.session_state.answers[q_index] - 1 if st.session_state.answers[q_index] is not None else 0))
    else:
        answer = st.text_area("Your answer:", 
                            value=st.session_state.answers[q_index] if st.session_state.answers[q_index] is not None else "",
                            height=100)
    
    # Navigation buttons
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if q_index > 0 and st.button("Previous"):
            # Record time spent on current question
            time_spent = time.time() - st.session_state.last_question_time
            st.session_state.question_times[q_index] += time_spent
            st.session_state.answers[q_index] = answer
            st.session_state.current_question -= 1
            st.session_state.last_question_time = time.time()
            st.rerun()
    
    with col2:
        if st.button("Save Progress"):
            # Record time spent on current question
            time_spent = time.time() - st.session_state.last_question_time
            st.session_state.question_times[q_index] += time_spent
            st.session_state.answers[q_index] = answer
            st.session_state.last_question_time = time.time()
            st.success("Progress saved!")
    
    with col3:
        if q_index < len(SURVEY_QUESTIONS) - 1 and st.button("Next"):
            # Record time spent on current question
            time_spent = time.time() - st.session_state.last_question_time
            st.session_state.question_times[q_index] += time_spent
            st.session_state.answers[q_index] = answer
            st.session_state.current_question += 1
            st.session_state.last_question_time = time.time()
            st.rerun()
        elif q_index == len(SURVEY_QUESTIONS) - 1 and st.button("Submit Survey"):
            # Record time spent on current question
            time_spent = time.time() - st.session_state.last_question_time
            st.session_state.question_times[q_index] += time_spent
            st.session_state.answers[q_index] = answer
            st.session_state.survey_complete = True
            st.rerun()

def show_results():
    """Display survey results and send email"""
    st.success("Survey completed! Thank you for your time.")
    
    # Prepare answers data
    answers_data = []
    for i, question in enumerate(SURVEY_QUESTIONS):
        answers_data.append({
            "question": question,
            "answer": st.session_state.answers[i],
            "time_spent": st.session_state.question_times[i]
        })
    
    # Display results
    st.subheader("Your Answers:")
    for item in answers_data:
        st.markdown(f"**{item['question']}**")
        st.write(f"Answer: {item['answer']}")
        if st.session_state.mode == "relaxed":
            st.write(f"Time spent: {item['time_spent']:.1f} seconds")
        st.write("---")
    
    # Send email
    if st.button("Submit Final Answers"):
        if send_email(answers_data):
            st.success("Answers submitted successfully!")
        else:
            st.error("Failed to submit answers. Please try again later.")

def main():
    st.set_page_config(page_title="Survey App", page_icon="📋", layout="wide")
    
    # Custom CSS for better styling
    st.markdown("""
    <style>
        .stProgress > div > div > div > div {
            background-color: #4CAF50;
        }
        .st-bb {
            background-color: #f0f2f6;
        }
        .st-at {
            background-color: #4CAF50;
        }
        .css-1aumxhk {
            background-color: #f0f2f6;
            background-image: none;
        }
        .big-font {
            font-size:20px !important;
            font-weight: bold;
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.title("📋 Survey Application")
    
    # Mode selection if not already chosen
    if st.session_state.mode is None:
        st.markdown("### Select Survey Mode")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### ⏱️ Timer Mode")
            st.markdown("- Fixed time per question")
            st.markdown("- No going back to previous questions")
            st.markdown("- Designed to measure quick responses")
            if st.button("Start Timer Mode"):
                st.session_state.mode = "timer"
                st.session_state.current_question = 0
                st.session_state.timer_start = time.time()
                st.rerun()
        
        with col2:
            st.markdown("#### 😌 Relaxed Mode")
            st.markdown("- No time pressure")
            st.markdown("- Navigate freely between questions")
            st.markdown("- Time spent on each question is measured")
            if st.button("Start Relaxed Mode"):
                st.session_state.mode = "relaxed"
                st.session_state.current_question = 0
                st.session_state.last_question_time = time.time()
                st.rerun()
        
        return
    
    # Survey in progress
    if not hasattr(st.session_state, 'survey_complete') or not st.session_state.survey_complete:
        st.sidebar.markdown(f"### Survey Mode: {'⏱️ Timer' if st.session_state.mode == 'timer' else '😌 Relaxed'}")
        
        if st.session_state.mode == "timer":
            # Timer mode settings in sidebar
            st.session_state.time_per_question = st.sidebar.slider(
                "Seconds per question:", 
                min_value=10, 
                max_value=120, 
                value=30,
                key="timer_slider"
            )
            
            if st.sidebar.button("Restart Survey"):
                st.session_state.answers = {i: None for i in range(len(SURVEY_QUESTIONS))}
                st.session_state.current_question = 0
                st.session_state.timer_start = time.time()
                st.rerun()
            
            display_question_timer_mode(st.session_state.current_question)
        
        else:  # Relaxed mode
            if st.sidebar.button("Restart Survey"):
                st.session_state.answers = {i: None for i in range(len(SURVEY_QUESTIONS))}
                st.session_state.question_times = {i: 0 for i in range(len(SURVEY_QUESTIONS))}
                st.session_state.current_question = 0
                st.session_state.last_question_time = time.time()
                st.rerun()
            
            # Question navigation in sidebar
            st.sidebar.markdown("### Navigation")
            for i, question in enumerate(SURVEY_QUESTIONS):
                status = "✅" if st.session_state.answers[i] is not None else "❌"
                if st.sidebar.button(f"{status} Q{i+1}: {question[:20]}...", key=f"nav_{i}"):
                    # Record time spent on current question before navigating
                    if 'last_question_time' in st.session_state:
                        time_spent = time.time() - st.session_state.last_question_time
                        st.session_state.question_times[st.session_state.current_question] += time_spent
                    
                    st.session_state.current_question = i
                    st.session_state.last_question_time = time.time()
                    st.rerun()
            
            display_question_relaxed_mode(st.session_state.current_question)
    
    else:
        show_results()

if __name__ == "__main__":
    main()