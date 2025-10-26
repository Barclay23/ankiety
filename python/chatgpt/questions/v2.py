import streamlit as st
import time

# Sample questions
QUESTIONS = [
    {"question": "What is your favorite color?", "options": ["Red", "Green", "Blue", "Yellow"]},
    {"question": "What is your preferred pet?", "options": ["Dog", "Cat", "Bird", "Fish"]},
    {"question": "Which season do you like most?", "options": ["Spring", "Summer", "Autumn", "Winter"]},
]

TIMER_DURATION = 10  # seconds per question in timer mode


def init_session():
    if "mode" not in st.session_state:
        st.session_state.mode = "not_started"
        st.session_state.timer_index = 0
        st.session_state.relaxed_index = 0
        st.session_state.answers_timer = [None] * len(QUESTIONS)
        st.session_state.answers_relaxed = [None] * len(QUESTIONS)
        st.session_state.relaxed_start_times = [None] * len(QUESTIONS)
        st.session_state.relaxed_durations = [0] * len(QUESTIONS)
        st.session_state.timer_completed = False


def run_timer_mode():
    index = st.session_state.timer_index
    question = QUESTIONS[index]

    st.subheader(f"Timer Mode - Question {index + 1} of {len(QUESTIONS)}")
    st.markdown("You must answer quickly. Time is running out!")

    # Timer UI
    label_placeholder = st.empty()
    progress_bar = st.empty()
    start_time = time.time()
    elapsed = 0

    while elapsed < TIMER_DURATION:
        elapsed = time.time() - start_time
        remaining_time = max(0, TIMER_DURATION - int(elapsed))
        percent = max(0, int((TIMER_DURATION - elapsed) / TIMER_DURATION * 100))
        
        label_placeholder.markdown(f"⏳ Time left: **{remaining_time} seconds**")
        progress_bar.progress(percent)
        time.sleep(0.1)

    # Render question after timer
    selected = st.radio(question["question"], question["options"], key=f"timer_q_{index}")
    st.session_state.answers_timer[index] = selected

    # Navigation
    if index + 1 < len(QUESTIONS):
        st.session_state.timer_index += 1
        st.rerun()
    else:
        st.session_state.mode = "relaxed"
        st.session_state.timer_completed = True
        st.rerun()



def run_relaxed_mode():
    index = st.session_state.relaxed_index
    question = QUESTIONS[index]
    st.subheader(f"Relaxed Mode - Question {index + 1} of {len(QUESTIONS)}")

    if st.session_state.relaxed_start_times[index] is None:
        st.session_state.relaxed_start_times[index] = time.time()

    answer = st.radio(question["question"], question["options"],
                      index=question["options"].index(st.session_state.answers_relaxed[index])
                      if st.session_state.answers_relaxed[index] else 0,
                      key=f"relaxed_q_{index}")
    st.session_state.answers_relaxed[index] = answer

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Previous", disabled=(index == 0)):
            st.session_state.relaxed_durations[index] += time.time() - st.session_state.relaxed_start_times[index]
            st.session_state.relaxed_index -= 1
            st.rerun()
    with col2:
        if st.button("Next", disabled=(index == len(QUESTIONS) - 1)):
            st.session_state.relaxed_durations[index] += time.time() - st.session_state.relaxed_start_times[index]
            st.session_state.relaxed_index += 1
            st.rerun()

    if index == len(QUESTIONS) - 1:
        if st.button("Finish Survey"):
            st.session_state.relaxed_durations[index] += time.time() - st.session_state.relaxed_start_times[index]
            st.session_state.mode = "completed"
            st.rerun()


def show_summary():
    st.title("Survey Completed")
    st.subheader("Your Answers:")

    for i, q in enumerate(QUESTIONS):
        st.write(f"**Q{i + 1}: {q['question']}**")
        st.write(f"Timer Mode Answer: `{st.session_state.answers_timer[i]}`")
        st.write(f"Relaxed Mode Answer: `{st.session_state.answers_relaxed[i]}`")
        st.write(f"Time Spent in Relaxed Mode: `{st.session_state.relaxed_durations[i]:.2f}` seconds")
        st.markdown("---")


def main():
    st.set_page_config(page_title="Survey App", layout="centered")
    st.title("📝 Survey Application")

    init_session()

    if st.session_state.mode == "not_started":
        if st.button("Start Timer Mode"):
            st.session_state.mode = "timer"
            st.rerun()
        st.warning("You must complete Timer Mode first to unlock Relaxed Mode.")

    elif st.session_state.mode == "timer":
        run_timer_mode()

    elif st.session_state.mode == "relaxed":
        st.success("Timer Mode completed. Now continue with Relaxed Mode.")
        run_relaxed_mode()

    elif st.session_state.mode == "completed":
        show_summary()


if __name__ == "__main__":
    main()
