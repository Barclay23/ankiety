import streamlit as st
import time
import smtplib
from email.mime.text import MIMEText

# Configuration
EMAIL_TO = "your_email@example.com"  # Replace with the target email
QUESTIONS = [
    "What is your name?",
    "How do you rate your experience on a scale from 1 to 10?",
    "What improvements would you suggest?",
]

def send_email(answers):
    message = "Survey Answers:\n\n" + "\n".join([f"Q{i+1}: {q}\nA{i+1}: {a}" for i, (q, a) in enumerate(answers.items())])
    msg = MIMEText(message)
    msg["Subject"] = "Survey Responses"
    msg["From"] = "survey_app@example.com"
    msg["To"] = EMAIL_TO
    
    with smtplib.SMTP("smtp.example.com") as server:  # Replace with actual SMTP server
        server.sendmail(msg["From"], [EMAIL_TO], msg.as_string())

def timer_mode():
    st.title("Survey - Timer Mode")
    answers = {}
    for idx, question in enumerate(QUESTIONS):
        st.subheader(question)
        start_time = time.time()
        answer = st.text_input(f"Answer {idx+1}")
        time_left = 15  # 15 seconds per question
        while time.time() - start_time < time_left:
            st.warning(f"Time left: {time_left - int(time.time() - start_time)}s")
            time.sleep(1)
        answers[question] = answer
    send_email(answers)
    st.success("Survey submitted successfully!")

def relaxed_mode():
    st.title("Survey - Relaxed Mode")
    answers = {}
    times = {}
    idx = 0
    while idx < len(QUESTIONS):
        st.subheader(QUESTIONS[idx])
        start_time = time.time()
        answer = st.text_input(f"Answer {idx+1}", answers.get(QUESTIONS[idx], ""))
        if st.button("Next"):
            times[QUESTIONS[idx]] = time.time() - start_time
            answers[QUESTIONS[idx]] = answer
            idx += 1
        if idx > 0 and st.button("Back"):
            idx -= 1
    send_email(answers)
    st.success("Survey submitted successfully!")

def main():
    st.sidebar.title("Survey Settings")
    mode = st.sidebar.radio("Choose mode:", ["Timer Mode", "Relaxed Mode"])
    if mode == "Timer Mode":
        timer_mode()
    else:
        relaxed_mode()

if __name__ == "__main__":
    main()
