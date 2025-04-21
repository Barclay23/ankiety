import streamlit as st
import time

# --- Inject CSS for styling ---
def inject_css():
    st.markdown(
        """
        <style>
            /* Base background and text color */
            .stApp {
                background-color: #003366 !important;
                color: white !important;
            }

            /* Global font color overrides */
            html, body, [class*="css"] {
                color: white !important;
            }

            /* Markdown, headers, and general elements */
            .stMarkdown, .stText, .stCaption, .stSubheader, .stTitle, .stHeader {
                color: white !important;
            }

            /* Headings */
            h1, h2, h3, h4, h5, h6 {
                color: white !important;
            }

            /* Radio buttons and their labels */
            .stRadio > div {
                background-color: #004080 !important;
                border-radius: 8px;
                padding: 10px;
            }

            .stRadio label {
                color: white !important;
                font-weight: 500;
            }

            /* Buttons */
            .stButton > button {
                background-color: #0059b3 !important;
                color: white !important;
                border: none;
                border-radius: 5px;
            }

            .stButton > button:hover {
                background-color: #004080 !important;
            }

            /* Progress bar color */
            .stProgress > div > div {
                background-color: #66b3ff !important;
            }

            /* DataFrame or other result tables (if ever used) */
            .stDataFrame, .dataframe {
                color: white !important;
            }

            /* Inputs and select elements */
            label, input, textarea, select {
                color: white !important;
                background-color: #004080 !important;
                border: 1px solid #0073e6 !important;
            }

            /* Improve dropdown/select readability */
            .css-1wa3eu0-placeholder, .css-1uccc91-singleValue {
                color: white !important;
            }
        </style>
        """,
        unsafe_allow_html=True
    )



# --- Constants ---
TIMER_SECONDS = 10
QUESTIONS = [
    {
        "type": "single",
        "question": "What is the capital of France?",
        "options": ["Berlin", "Madrid", "Paris", "Rome"],
        "follow_up": {
            "trigger_answer": "Paris",
            "question": {
                "type": "open",
                "question": "What do you like most about Paris?"
            }
        }
    },
    {
        "type": "single",
        "question": "Which language is primarily spoken in Brazil?",
        "options": ["Portuguese", "Spanish", "English", "French"]
    },
    {
        "type": "single",
        "question": "What is 5 + 7?",
        "options": ["10", "11", "12", "13"]
    },
    {
        "type": "multi",
        "question": "Select the prime numbers:",
        "options": ["2", "4", "5", "9", "11"]
    },
    {
        "type": "open",
        "question": "Briefly describe your ideal vacation."
    }
]

def render_question(question, key_prefix):
    q_type = question.get("type", "single")
    key = f"{key_prefix}_{st.session_state.question_index}"

    if q_type == "single":
        return st.radio("Select an answer:", question["options"], key=key)
    elif q_type == "multi":
        return st.multiselect("Select all that apply:", question["options"], key=key)
    elif q_type == "open":
        return st.text_area("Your answer:", key=key)
    else:
        st.error("Unknown question type.")
        return None

# --- Session State Initialization ---
if "dynamic_questions" not in st.session_state:
    st.session_state.dynamic_questions = list(QUESTIONS)  # Clone the original list
    for q in QUESTIONS:
        if "follow_up" in q:
            q["follow_up_inserted"] = False

if "mode" not in st.session_state:
    st.session_state.mode = "timer"
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


def go_to_next_question(selected_answer=None):
    q_idx = st.session_state.question_index
    current_question = st.session_state.dynamic_questions[q_idx]

    # Store the answer
    mode = st.session_state.mode
    if len(st.session_state.answers[mode]) > q_idx:
        st.session_state.answers[mode][q_idx] = selected_answer
    else:
        st.session_state.answers[mode].append(selected_answer)

    elapsed = time.time() - st.session_state.start_time if st.session_state.start_time else 0
    if len(st.session_state.times[mode]) > q_idx:
        st.session_state.times[mode][q_idx] = round(elapsed, 2)
    else:
        st.session_state.times[mode].append(round(elapsed, 2))

    # Only add follow-up once
    if current_question.get("follow_up") and not current_question.get("follow_up_inserted"):
        if selected_answer == current_question["follow_up"]["trigger_answer"]:
            st.session_state.dynamic_questions.insert(
                q_idx + 1, current_question["follow_up"]["question"]
            )
            current_question["follow_up_inserted"] = True

    # Proceed
    st.session_state.question_index += 1
    st.session_state.start_time = None
    st.session_state.timer_expired = False
    st.rerun()




def timer_mode():
    st.title("🕒 Survey - Timer Mode")
    q_idx = st.session_state.question_index
    question = st.session_state.dynamic_questions[q_idx]

    st.markdown(f"**Question {q_idx + 1}:** {question['question']}")
    selected = render_question(question, "timer")

    if st.session_state.start_time is None:
        st.session_state.start_time = time.time()

    elapsed = time.time() - st.session_state.start_time
    remaining = TIMER_SECONDS - elapsed

    if remaining > 0:
        st.progress(remaining / TIMER_SECONDS)
        st.caption(f"Time remaining: {int(remaining)}s")
        time.sleep(1)
        st.rerun()
    else:
        if not st.session_state.timer_expired:
            st.session_state.timer_expired = True
            st.session_state.answers["timer"].append(selected)
            st.session_state.times["timer"].append(round(elapsed, 2))

            if q_idx + 1 < len(st.session_state.dynamic_questions):
                go_to_next_question(selected)
            else:
                st.session_state.mode = "relaxed"
                st.session_state.question_index = 0
                st.session_state.start_time = None
                st.rerun()


def relaxed_mode():
    st.title("😌 Survey - Relaxed Mode")
    q_idx = st.session_state.question_index
    question = st.session_state.dynamic_questions[q_idx]

    st.markdown(f"**Question {q_idx + 1}:** {question['question']}")
    if st.session_state.start_time is None:
        st.session_state.start_time = time.time()

    selected = render_question(question, "relaxed")

    col1, col2 = st.columns([1, 1])
    if col1.button("⬅ Previous") and q_idx > 0:
        st.session_state.question_index -= 1
        st.session_state.start_time = None
        st.rerun()

    if col2.button("Next ➡"):
        elapsed = time.time() - st.session_state.start_time

        if len(st.session_state.answers["relaxed"]) > q_idx:
            st.session_state.answers["relaxed"][q_idx] = selected
            st.session_state.times["relaxed"][q_idx] = round(elapsed, 2)
        else:
            st.session_state.answers["relaxed"].append(selected)
            st.session_state.times["relaxed"].append(round(elapsed, 2))

        if q_idx + 1 < len(st.session_state.dynamic_questions):
            go_to_next_question(selected)
        else:
            show_results()



def show_results():
    st.title("✅ Survey Completed")
    st.subheader("Your Answers and Time Spent")

    st.markdown("### ⏱ Timer Mode")
    for i, (ans, secs) in enumerate(zip(st.session_state.answers["timer"], st.session_state.times["timer"])):
        st.markdown(f"<p style='color:white'><strong>Q{i+1}:</strong> {ans} <em>(Time: {secs:.2f}s)</em></p>", unsafe_allow_html=True)

    st.markdown("### 😌 Relaxed Mode")
    for i, (ans, secs) in enumerate(zip(st.session_state.answers["relaxed"], st.session_state.times["relaxed"])):
        st.markdown(f"<p style='color:white'><strong>Q{i+1}:</strong> {ans} <em>(Time: {secs:.2f}s)</em></p>", unsafe_allow_html=True)

    st.success("🎉 Thank you for completing the survey!")
    st.stop()


# --- Main ---
inject_css()

if st.session_state.mode == "timer":
    timer_mode()
elif st.session_state.mode == "relaxed":
    relaxed_mode()
