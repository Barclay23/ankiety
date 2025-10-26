import streamlit as st
import time

# --- Constants ---
TIMER_SECONDS = 10
QUESTIONS = [
    {"question": "What is the capital of France?", "options": ["Berlin", "Madrid", "Paris", "Rome"]},
    {"question": "Which language is primarily spoken in Brazil?", "options": ["Portuguese", "Spanish", "English", "French"]},
    {"question": "What is 5 + 7?", "options": ["10", "11", "12", "13"]},
]

# --- Session State Initialization ---
if "mode" not in st.session_state:
    st.session_state.mode = "timer"  # "timer" or "relaxed"
if "answers" not in st.session_state:
    st.session_state.answers = {"timer": [], "relaxed": []}
if "question_index" not in st.session_state:
    st.session_state.question_index = 0
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "times" not in st.session_state:
    st.session_state.times = {"timer": [], "relaxed": []}
if "timer_expired" not in st.session_state:
    st.session_state.timer_expired = False


def go_to_next_question():
    st.session_state.question_index += 1
    st.session_state.start_time = None
    st.session_state.timer_expired = False
    st.rerun()


def timer_mode():
    st.title("Survey - Timer Mode")
    q_idx = st.session_state.question_index
    question = QUESTIONS[q_idx]

    st.write(f"**Question {q_idx + 1}:** {question['question']}")
    selected = st.radio("Select an answer:", question["options"], key=f"timer_{q_idx}")

    # Start timer only once
    if st.session_state.start_time is None:
        st.session_state.start_time = time.time()

    # Timer display
    elapsed = time.time() - st.session_state.start_time
    remaining = TIMER_SECONDS - elapsed

    if remaining > 0:
        progress = remaining / TIMER_SECONDS
        st.progress(progress)
        st.caption(f"Time remaining: {int(remaining)}s")
        # Rerun after short pause to simulate countdown
        time.sleep(1)
        st.rerun()
    else:
        if not st.session_state.timer_expired:
            # Save answer and move forward
            st.session_state.timer_expired = True
            st.session_state.answers["timer"].append(selected if selected else None)
            st.session_state.times["timer"].append(round(elapsed, 2))

            if q_idx + 1 < len(QUESTIONS):
                go_to_next_question()
            else:
                # Switch to relaxed mode
                st.session_state.mode = "relaxed"
                st.session_state.question_index = 0
                st.session_state.start_time = None
                st.rerun()


def relaxed_mode():
    st.title("Survey - Relaxed Mode")
    q_idx = st.session_state.question_index
    question = QUESTIONS[q_idx]

    st.write(f"**Question {q_idx + 1}:** {question['question']}")
    if st.session_state.start_time is None:
        st.session_state.start_time = time.time()

    selected = st.radio("Select an answer:", question["options"], key=f"relaxed_{q_idx}")

    col1, col2 = st.columns([1, 1])
    if col1.button("Previous") and q_idx > 0:
        st.session_state.question_index -= 1
        st.session_state.start_time = None
        st.rerun()

    if col2.button("Next"):
        elapsed = time.time() - st.session_state.start_time

        if len(st.session_state.answers["relaxed"]) > q_idx:
            st.session_state.answers["relaxed"][q_idx] = selected
            st.session_state.times["relaxed"][q_idx] = round(elapsed, 2)
        else:
            st.session_state.answers["relaxed"].append(selected)
            st.session_state.times["relaxed"].append(round(elapsed, 2))

        if q_idx + 1 < len(QUESTIONS):
            go_to_next_question()
        else:
            show_results()


def show_results():
    st.title("Survey Completed 🎉")
    st.subheader("Your Answers and Time Spent")

    st.write("**Timer Mode:**")
    for i, (ans, secs) in enumerate(zip(st.session_state.answers["timer"], st.session_state.times["timer"])):
        st.write(f"Q{i+1}: {ans} (Time: {secs:.2f}s)")

    st.write("**Relaxed Mode:**")
    for i, (ans, secs) in enumerate(zip(st.session_state.answers["relaxed"], st.session_state.times["relaxed"])):
        st.write(f"Q{i+1}: {ans} (Time: {secs:.2f}s)")

    st.success("Thank you for completing the survey!")
    st.stop()


# --- Main ---
if st.session_state.mode == "timer":
    timer_mode()
elif st.session_state.mode == "relaxed":
    relaxed_mode()
