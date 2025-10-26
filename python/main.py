import streamlit as st
import time
import pandas as pd

def main():
    st.title("Ankieta")

    # Przycisk startowy
    if 'quiz_started' not in st.session_state:
        st.session_state.quiz_started = False

    if not st.session_state.quiz_started:
        if st.button("Rozpocznij quiz"):
            st.session_state.quiz_started = True
            st.session_state.question_index = 0  # Resetujemy indeks pytania
            st.session_state.answers1 = {}  # Resetujemy odpowiedzi z pierwszej rundy
            st.session_state.answers2 = {}  # Resetujemy odpowiedzi z drugiej rundy
            st.session_state.timer = time.time()  # Resetujemy licznik czasu
            st.session_state.which = 1  # Ustawiamy tryb pierwszej rundy
            st.rerun()
        return

    # Lista pytań i odpowiedzi
    questions = [
        {"question": "Jaki jest największy ocean na świecie?", "options": ["Atlantycki", "Spokojny", "Arktyczny", "Indyjski"], "correct": "Spokojny"},
        {"question": "Które z tych zwierząt jest ssakiem?", "options": ["Żaba", "Rekin", "Delfin", "Wąż"], "correct": "Delfin"},
        {"question": "Ile wynosi wartość liczby Pi z dokładnością do dwóch miejsc po przecinku?", "options": ["3.12", "3.14", "3.16", "3.18"], "correct": "3.14"}
    ]

    question_time = 3  # Czas na odpowiedź w pierwszej rundzie

    if 'question_index' not in st.session_state:
        st.session_state.question_index = 0
    if 'answers1' not in st.session_state:
        st.session_state.answers1 = {}
    if 'answers2' not in st.session_state:
        st.session_state.answers2 = {}
    if 'timer' not in st.session_state:
        st.session_state.timer = time.time()
    if 'answers2timer' not in st.session_state:
        st.session_state.answers2timer = {i: 0 for i in range(len(questions))}
    if 'start_time' not in st.session_state:
        st.session_state.start_time = {i: None for i in range(len(questions))}
    if 'which' not in st.session_state:
        st.session_state.which = 1

    index = st.session_state.question_index

    if st.session_state.which == 1:  # Pierwsza runda (quiz z limitem czasu)
        if index < len(questions):
            question = questions[index]
            st.write(f"### Pytanie {index + 1}: {question['question']}")

            # Licznik czasu
            time_left = max(0, question_time - int(time.time() - st.session_state.timer))
            st.write(f"⏳ Pozostały czas: {time_left} sekundy")
            st.progress(time_left / question_time)

            answer = st.radio("Wybierz odpowiedź:", question['options'], index=None, key=f"q1_{index}")

            if time_left == 0 or st.button("Zatwierdź odpowiedź") or answer:
                st.session_state.answers1[index] = answer if answer else "Brak odpowiedzi"
                st.session_state.question_index += 1
                st.session_state.timer = time.time()

                if st.session_state.question_index == len(questions):  # Koniec pierwszej rundy
                    st.session_state.question_index = 0  # Resetujemy indeks pytania
                    st.session_state.which = 2  # Przechodzimy do drugiej rundy

                st.rerun()
            else:
                time.sleep(1)
                st.rerun()

    elif st.session_state.which == 2:  # Druga runda (ankieta bez limitu czasu, możliwość powrotu)
        question = questions[index]
        st.write(f"### Pytanie {index + 1}: {question['question']}")

        # Rozpoczęcie pomiaru czasu dla pytania (jeśli nie było jeszcze odwiedzone)
        if st.session_state.start_time[index] is None:
            st.session_state.start_time[index] = time.time()

        answer = st.radio(
            "Wybierz odpowiedź:",
            question['options'],
            index=question['options'].index(st.session_state.answers2.get(index, "Brak odpowiedzi")) if index in st.session_state.answers2 else None,
            key=f"q2_{index}"
        )

        if answer:
            st.session_state.answers2[index] = answer

        col1, col2 = st.columns(2)

        with col1:
            if index != 0:
                if st.button("⬅️ Poprzednie pytanie") and index > 0:
                    end_time = time.time()
                    st.session_state.answers2timer[index] += end_time - st.session_state.start_time[index]
                    st.session_state.start_time[index] = None  # Resetujemy start dla kolejnego odwiedzenia
                    st.session_state.question_index -= 1
                    st.rerun()

        with col2:
            if index != len(questions) - 1:
                if st.button("➡️ Następne pytanie") and index < len(questions) - 1: 
                    # Zapisujemy czas spędzony na tym pytaniu
                    end_time = time.time()
                    st.session_state.answers2timer[index] += end_time - st.session_state.start_time[index]
                    st.session_state.start_time[index] = None  # Resetujemy start dla kolejnego odwiedzenia
                    st.session_state.question_index += 1
                    st.rerun()

        with col2:
            if index == len(questions) - 1 and st.button("Zakończ ankietę"):
                # Zapisujemy czas ostatniego pytania
                end_time = time.time()
                st.session_state.answers2timer[index] += end_time - st.session_state.start_time[index]
                st.session_state.start_time[index] = None
                st.session_state.which = 3  # Przejście do wyników
                st.rerun()


    elif st.session_state.which == 3:  # Wyniki końcowe
        st.write("### Wyniki:")
        
        results = []
        for i, question in enumerate(questions):
            results.append({
                "Pytanie": question['question'],
                "Twoja odpowiedź": st.session_state.answers2.get(i, 'Brak odpowiedzi'),
                "Poprawna odpowiedź": question['correct'],
                "Czas (sekundy)": round(st.session_state.answers2timer[i], 2)
            })

        df = pd.DataFrame(results)
        st.dataframe(df)

if __name__ == "__main__":
    main()
