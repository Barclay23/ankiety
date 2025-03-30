import streamlit as st
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from datetime import datetime

class SurveyApp:
    def __init__(self):
        # Configuration
        self.ADMIN_EMAIL = "survey.admin@example.com"  # Replace with actual email
        self.SMTP_SERVER = "smtp.gmail.com"  # Replace with your SMTP server
        self.SMTP_PORT = 587  # Typical port for TLS
        
        # Survey questions
        self.questions = [
            "What motivates you most in your work?",
            "How do you handle stress in challenging situations?", 
            "Describe a professional achievement you're proud of.",
            "What skills are you looking to develop in the next year?",
            "How do you approach learning new technologies?"
        ]
        
        # Initialize session state
        if 'mode' not in st.session_state:
            st.session_state.mode = None
        if 'answers' not in st.session_state:
            st.session_state.answers = {}
        if 'question_times' not in st.session_state:
            st.session_state.question_times = {}
        if 'current_question' not in st.session_state:
            st.session_state.current_question = 0

    def send_email(self, answers, total_time):
        """Send survey results via email"""
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = "survey.app@example.com"
            msg['To'] = self.ADMIN_EMAIL
            msg['Subject'] = f"Survey Results - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

            # Compile body
            body = "Survey Results:\n\n"
            for q, a in answers.items():
                body += f"Q: {q}\nA: {a}\n\n"
            body += f"Total Survey Time: {total_time:.2f} seconds"

            msg.attach(MIMEText(body, 'plain'))

            # Send email (you'll need to configure SMTP credentials securely)
            # server = smtplib.SMTP(self.SMTP_SERVER, self.SMTP_PORT)
            # server.starttls()
            # server.login(USERNAME, PASSWORD)
            # server.send_message(msg)
            # server.quit()

            st.success("Survey submitted successfully!")
        except Exception as e:
            st.error(f"Error sending email: {e}")

    def timer_mode(self):
        """Timer mode with strict time limits"""
        st.header("🕒 Timer Mode")
        
        # Time limit per question (in seconds)
        TIME_LIMIT = 30
        
        # Current question
        current_q = self.questions[st.session_state.current_question]
        
        # Start timer
        placeholder = st.empty()
        progress_bar = st.progress(0)
        
        # Timer logic
        start_time = time.time()
        while time.time() - start_time < TIME_LIMIT:
            remaining = TIME_LIMIT - (time.time() - start_time)
            placeholder.metric("Time Remaining", f"{remaining:.1f} seconds")
            progress_bar.progress(1 - (remaining / TIME_LIMIT))
            
            # Answer input
            answer = st.text_area(f"Question {st.session_state.current_question + 1}: {current_q}", key=f"timer_q{st.session_state.current_question}")
            
            # Submit button
            if st.button("Next Question"):
                st.session_state.answers[current_q] = answer
                st.session_state.current_question += 1
                break
            
            time.sleep(0.1)
        
        # Time expired
        if time.time() - start_time >= TIME_LIMIT:
            st.warning("Time's up! Moving to next question.")
            st.session_state.answers[current_q] = st.session_state.get(f"timer_q{st.session_state.current_question}", "")
            st.session_state.current_question += 1
        
        # Check if survey is complete
        if st.session_state.current_question >= len(self.questions):
            self.send_email(st.session_state.answers, time.time() - start_time)
            st.session_state.current_question = 0
            st.session_state.answers = {}

    def relaxed_mode(self):
        """Relaxed mode with flexible answering"""
        st.header("😌 Relaxed Mode")
        
        # Track time for each question
        if 'start_time' not in st.session_state:
            st.session_state.start_time = time.time()
        
        # Current question
        current_q = self.questions[st.session_state.current_question]
        
        # Navigation options
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Previous Question") and st.session_state.current_question > 0:
                st.session_state.current_question -= 1
        
        with col2:
            if st.button("Next Question"):
                # Calculate time spent on current question
                current_time = time.time()
                question_time = current_time - st.session_state.start_time
                st.session_state.question_times[current_q] = question_time
                
                st.session_state.current_question += 1
                st.session_state.start_time = current_time
        
        # Answer input with previous answer retention
        current_q = self.questions[st.session_state.current_question]
        previous_answer = st.session_state.answers.get(current_q, "")
        answer = st.text_area(
            f"Question {st.session_state.current_question + 1}: {current_q}", 
            value=previous_answer,
            key=f"relaxed_q{st.session_state.current_question}"
        )
        
        # Save answer
        st.session_state.answers[current_q] = answer
        
        # Finish survey
        if st.session_state.current_question == len(self.questions) - 1:
            if st.button("Finish Survey"):
                total_time = sum(st.session_state.question_times.values())
                self.send_email(st.session_state.answers, total_time)
                st.session_state.current_question = 0
                st.session_state.answers = {}

    def main(self):
        """Main application flow"""
        st.title("🔍 Survey Application")
        
        # Mode selection
        st.session_state.mode = st.radio(
            "Select Survey Mode", 
            ["Select Mode", "Timer Mode", "Relaxed Mode"]
        )
        
        # Run appropriate mode
        if st.session_state.mode == "Timer Mode":
            self.timer_mode()
        elif st.session_state.mode == "Relaxed Mode":
            self.relaxed_mode()

# Run the application
if __name__ == "__main__":
    app = SurveyApp()
    app.main()