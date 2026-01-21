import streamlit as st
import os
import json

from Programme.Konjugationstabelle import run_konjugationstabelle
from Programme.Wortschlange import run_Wortschlange
from Programme.Vokabelrätsel import run_Rätsel
from Programme.Vokabelsuchgitter import run_Vokabelsuchgitter
from Programme.worksheet_generator import generate_worksheets_streamlit
from Programme.Listen import Vokabellisten
from Programme.Worte_verbinden import Worte_zuordnen
from Programme.Konjugationen_Unterstriche import run_Unterstriche_Konjugationen

# ======================================================
# 📦 CACHING / FILE HELPERS (CLOUD-SICHER)
# ======================================================

@st.cache_data
def list_dirs(path):
    if not os.path.exists(path):
        return []
    return sorted([
        d for d in os.listdir(path)
        if os.path.isdir(os.path.join(path, d))
    ])

@st.cache_data
def list_json_files(path):
    if not os.path.exists(path):
        return []
    return sorted([
        f for f in os.listdir(path)
        if f.endswith(".json")
    ])

@st.cache_data
def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# ======================================================
# 📂 BASIS-PFADE
# ======================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

template_path = os.path.join(BASE_DIR, "Vorlagen", "Vorlage Vokabellisten.docx")
vokabel_folder = os.path.join(BASE_DIR, "Vokabeln")
kontext_folder = os.path.join(BASE_DIR, "Kontexte")
vocab_folder = os.path.join(vokabel_folder, "vocabs_all")
verbs_folder = os.path.join(BASE_DIR, "unregelmäßige Verben alle")

os.makedirs(vocab_folder, exist_ok=True)
os.makedirs(kontext_folder, exist_ok=True)

vocab_files = list_json_files(vocab_folder)

# ======================================================
# 🚀 STREAMLIT SETUP
# ======================================================

st.set_page_config(layout="wide")
st.title("Bonjour")

tab_diff, tab_verben, tab_vokabeln, tab_kontexte, tab_kl = st.tabs([
    "Differenzierungsmöglichkeiten",
    "wichtige Verben",
    "Vokabeln",
    "Kontexte",
    "Kontexte & Lernstand"
])

# ======================================================
# 1️⃣ DIFFERENZIERUNG
# ======================================================

with tab_diff:
    st.header("Differenzierungsmöglichkeiten")

    user_text = st.text_area(
        "Text eingeben ([Wörter] markieren)",
        height=200
    )

    if vocab_files:
        vocab_json = load_json(os.path.join(vocab_folder, vocab_files[0]))
    else:
        vocab_json = []

    if st.button("Arbeitsblatt erstellen", key="diff_create_worksheet") and user_text and vocab_json:
        file = generate_worksheets_streamlit(
            text=user_text,
            vocab_json=vocab_json,
            output_prefix="Differenzierung",
            selected_modules=[1, 2, 3],
            template_path=template_path
        )

        st.download_button(
            "⬇️ Arbeitsblatt herunterladen",
            file,
            "Differenzierung.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

# ======================================================
# 2️⃣ WICHTIGE VERBEN
# ======================================================

with tab_verben:
    json_files = list_json_files(verbs_folder)

    if not json_files:
        st.warning("Keine Verb-Dateien gefunden")
        st.stop()

    words_data = {}
    for f in json_files:
        words_data.update(load_json(os.path.join(verbs_folder, f)))

    all_verbs = sorted(words_data.keys())

    selected_verbs = st.multiselect(
        "Verben auswählen",
        all_verbs,
        default=all_verbs,
        key=f"verbs_{len(all_verbs)}"
    )

    if not selected_verbs:
        st.stop()

    times = list(words_data[selected_verbs[0]].keys())

    time1 = st.selectbox(
        "Zeitform 1",
        times,
        key=f"time1_{selected_verbs[0]}"
    )

    time2 = st.selectbox(
        "Zeitform 2",
        times,
        index=1 if len(times) > 1 else 0,
        key=f"time2_{selected_verbs[0]}"
    )

    rows = st.number_input("Zeilen", 1, 100, 20)

    if st.button("Arbeitsblatt erstellen", key="verbs_create_worksheet"):
        filtered = {v: words_data[v] for v in selected_verbs}

        file = run_Unterstriche_Konjugationen(
            filtered,
            rows,
            time1,
            time2,
            template_path
        )

        st.download_button(
            "⬇️ Word herunterladen",
            file,
            "Konjugationen_Unterstriche.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

# ======================================================
# 3️⃣ VOKABELN (KOMPLETT GEFIXT)
# ======================================================

with tab_vokabeln:
    books = list_dirs(vokabel_folder)

    if not books:
        st.warning("Keine Bücher gefunden")
        st.stop()

    book_tabs = st.tabs(books)

    for book, tab in zip(books, book_tabs):
        with tab:
            chapters = list_dirs(os.path.join(vokabel_folder, book))
            if not chapters:
                st.warning("Keine Kapitel")
                continue

            chapter = st.selectbox(
                "Kapitel",
                chapters,
                key=f"chapter_{book}_{hash(tuple(chapters))}"
            )

            chapter_path = os.path.join(vokabel_folder, book, chapter)
            files = list_json_files(chapter_path)

            if len(files) < 2:
                st.warning("Mindestens zwei JSON-Dateien")
                continue

            f1 = st.selectbox(
                "Datei 1",
                files,
                key=f"f1_{book}_{chapter}_{hash(tuple(files))}"
            )
            f2 = st.selectbox(
                "Datei 2",
                files,
                key=f"f2_{book}_{chapter}_{hash(tuple(files))}"
            )

            vocab_file = st.selectbox(
                "Wörterbuch",
                vocab_files,
                key=f"vocab_{book}_{chapter}"
            )

            # Kapitel-Dateien laden
            data1 = load_json(os.path.join(chapter_path, f1))
            data2 = load_json(os.path.join(chapter_path, f2))
            data = data1 + data2

            # Wörterbuch laden
            vocab_data = load_json(os.path.join(vocab_folder, vocab_file))

            # -------------------------------
            # Session-State initialisieren
            # -------------------------------
            session_key = f"selected_vocab_words_{book}_{chapter}"
            if session_key not in st.session_state:
                st.session_state[session_key] = []

            # Suche im Wörterbuch
            search_term = st.text_input(
                "Suche Wörter im Wörterbuch",
                key=f"search_vocab_{book}_{chapter}"
            )

            if st.button("Hinzufügen", key=f"add_vocab_{book}_{chapter}"):
                if search_term:
                    filtered = [
                        item for item in vocab_data
                        if search_term.lower() in item['word'].lower()
                    ]
                    st.session_state[session_key].extend(filtered)
                    # Dubletten entfernen
                    st.session_state[session_key] = list({
                        item['word']: item for item in st.session_state[session_key]
                    }.values())

            # Kapitel + gezielt ausgewählte Wörter zusammenführen
            merged_data = data + st.session_state[session_key]
            merged_data = [item for item in merged_data if 'word' in item and 'translation' in item]
            unique_data = list({item['word']: item for item in merged_data}.values())

            # Multiselect für Wörter
            selected_words = st.multiselect(
                "Wörter auswählen",
                [item["word"] for item in unique_data],
                default=[item["word"] for item in unique_data if item in st.session_state[session_key]],
                key=f"words_{book}_{chapter}_{len(unique_data)}"
            )

            # Wort-Translation-Paare
            words_dict = {item["word"]: item["translation"] for item in unique_data}
            word_pairs = [(word, words_dict[word]) for word in selected_words]

            # Programm auswählen
            program = st.selectbox(
                "Programm",
                ["Vokabelsuchgitter", "Vokabelrätsel", "Wortschlange", "Zuordnen", "Vokabelliste"],
                key=f"prog_{book}_{chapter}_{len(selected_words)}"
            )

            # AB erstellen
            if st.button("AB erstellen", key=f"run_{book}_{chapter}_{program}"):
                if not selected_words:
                    st.warning("Bitte zuerst Wörter auswählen!")
                else:
                    if program == "Wortschlange":
                        file = run_Wortschlange(word_pairs, template_path)
                    elif program == "Vokabelrätsel":
                        file = run_Rätsel(word_pairs, template_path)
                    elif program == "Vokabelsuchgitter":
                        file = run_Vokabelsuchgitter(word_pairs, template_path)
                    elif program == "Zuordnen":
                        file = Worte_zuordnen(word_pairs, template_path)
                    else:
                        file = Vokabellisten(word_pairs, template_path)

                    st.download_button(
                        "⬇️ Word herunterladen",
                        file,
                        f"{program}.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )

# ========================
# 4️⃣ Kontexte
# ========================
with tab_kontexte:
    st.header("Kontexte")

    kontext_files = [f for f in os.listdir(kontext_folder) if f.endswith(".json")]
    if not kontext_files:
        st.warning("Keine Kontext-Dateien gefunden!")
        st.stop()

    # Kontext-Datei auswählen
    selected_kontext_file = st.selectbox(
        "Wähle einen Kontext aus",
        kontext_files,
        key="selected_kontext"
    )

    kontext_data = load_json(os.path.join(kontext_folder, selected_kontext_file))

    # -------------------------------
    # Session-State für diese Kontext-Datei initialisieren
    # -------------------------------
    session_key = f"search_results_kontexte_{selected_kontext_file}"
    if session_key not in st.session_state:
        st.session_state[session_key] = []

    # 🔍 Suche im Wörterbuch
    search_term = st.text_input(
        "Suche Wörter im Wörterbuch",
        key=f"search_kontext_{selected_kontext_file}"
    )

    if st.button("Hinzufügen", key=f"add_kontext_vocab_{selected_kontext_file}"):
        if search_term:
            vocab_all_path = os.path.join(vocab_folder, "Wörterbuch.json")
            vocab_all_data = load_json(vocab_all_path)

            filtered = [
                item for item in vocab_all_data
                if search_term.lower() in item["word"].lower()
            ]

            st.session_state[session_key].extend(filtered)

            # Dubletten entfernen
            st.session_state[session_key] = list({
                item["word"]: item
                for item in st.session_state[session_key]
            }.values())

    # 🔗 Kontext + Suchergebnisse zusammenführen
    merged_data = kontext_data + st.session_state[session_key]
    merged_data = [item for item in merged_data if "word" in item and "translation" in item]
    unique_data = list({item["word"]: item for item in merged_data}.values())

    # ✅ Multiselect wie bei Vokabeln
    selected_words = st.multiselect(
        "Wörter auswählen",
        [item["word"] for item in unique_data],
        default=[item["word"] for item in st.session_state[session_key]],
        key=f"context_vocab_{selected_kontext_file}"
    )

    words_dict = {item["word"]: item["translation"] for item in unique_data}
    words_with_translations = [(word, words_dict[word]) for word in selected_words]

    programs = [
        "Vokabelsuchgitter",
        "Vokabelrätsel",
        "Wortschlange",
        "Zuordnen",
        "Vokabelliste"
    ]

    selected_program = st.selectbox(
        "Programm auswählen",
        programs,
        key=f"program_kontexte_{selected_kontext_file}"
    )

    if st.button("AB erstellen", key=f"run_kontext_{selected_kontext_file}_{selected_program}"):
        if not selected_words:
            st.warning("Bitte zuerst Wörter auswählen!")
        else:
            if selected_program == "Wortschlange":
                word_file = run_Wortschlange(words_with_translations, template_path)
            elif selected_program == "Vokabelrätsel":
                word_file = run_Rätsel(words_with_translations, template_path)
            elif selected_program == "Vokabelsuchgitter":
                word_file = run_Vokabelsuchgitter(words_with_translations, template_path)
            elif selected_program == "Vokabelliste":
                word_file = Vokabellisten(words_with_translations, template_path)
            elif selected_program == "Zuordnen":
                word_file = Worte_zuordnen(words_with_translations, template_path)

            st.download_button(
                "Word-Datei herunterladen",
                word_file,
                f"{selected_program}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                key=f"download_kontext_{selected_kontext_file}_{selected_program}"
            )

# ========================
# 5️⃣ Kontexte & Lernstand
# ========================

with tab_kl:
    st.header("Kontexte & Lernstand")

    # --------------------------------------------------
    # Session State initialisieren
    # --------------------------------------------------
    if "kl_search_results" not in st.session_state:
        st.session_state.kl_search_results = []

    # --------------------------------------------------
    # Kontext auswählen
    # --------------------------------------------------
    selected_kontext_file = st.selectbox(
        "Wähle einen Kontext",
        kontext_files,
        key="kl_selected_kontext_file"
    )

    kontext_path = os.path.join(kontext_folder, selected_kontext_file)
    kontext_data = load_json(kontext_path)  # ✅ LISTE von dicts

    # --------------------------------------------------
    # Lernstand auswählen
    # --------------------------------------------------
    num = st.slider(
        "Wähle die Anzahl der Lernstände",
        min_value=1,
        max_value=81,
        value=1,
        step=1,
        key="kl_lernstand_slider"
    )

    # --------------------------------------------------
    # Lernstände laden
    # --------------------------------------------------
    lernstand_data = []
    for i in range(1, num + 1):
        try:
            file_path = os.path.join(kontext_folder, "Vokabeln", f"{i}.json")
            lernstand_data.extend(load_json(file_path))
        except FileNotFoundError:
            st.warning(f"Lernstand {i} nicht gefunden.")

    # --------------------------------------------------
    # 🔹 Kontext-Vokabeln filtern (nur im Lernstand)
    # --------------------------------------------------
    lernstand_words = {
        item["word"].lower()
        for item in lernstand_data
        if "word" in item
    }

    kontext_vocab_gefiltert = [
        item for item in kontext_data
        if item.get("word", "").lower() in lernstand_words
    ]

    # --------------------------------------------------
    # 🔹 Suche im Wörterbuch
    # --------------------------------------------------
    search_term = st.text_input(
        "Suche Wörter im Wörterbuch",
        key="kl_search_term"
    )

    if st.button("Hinzufügen", key="kl_add_vocab_button"):
        if search_term:
            vocab_all_path = os.path.join(
                vocab_folder,
                "Wörterbuch.json"
            )
            vocab_all_data = load_json(vocab_all_path)

            filtered = [
                item for item in vocab_all_data
                if search_term.lower() in item["word"].lower()
            ]

            st.session_state.kl_search_results.extend(filtered)

            # Dubletten entfernen
            st.session_state.kl_search_results = list({
                item["word"]: item
                for item in st.session_state.kl_search_results
                if "word" in item
            }.values())

    # --------------------------------------------------
    # 🔗 Kontext + Suchergebnisse zusammenführen
    # --------------------------------------------------
    merged_data = (
        kontext_vocab_gefiltert
        + st.session_state.kl_search_results
    )

    merged_data = [
        item for item in merged_data
        if "word" in item and "translation" in item
    ]

    unique_data = list({
        item["word"]: item
        for item in merged_data
    }.values())

    # --------------------------------------------------
    # Multiselect
    # --------------------------------------------------
    selected_words = st.multiselect(
        "Wörter auswählen",
        [item["word"] for item in unique_data],
        default=[item["word"] for item in unique_data],
        key="kl_selected_words"
    )

    words_dict = {
        item["word"]: item["translation"]
        for item in unique_data
    }

    words_with_translations = [
        (word, words_dict[word])
        for word in selected_words
    ]

    # --------------------------------------------------
    # Programme auswählen
    # --------------------------------------------------
    programs = [
        "Vokabelsuchgitter",
        "Vokabelrätsel",
        "Wortschlange",
        "Zuordnen",
        "Vokabelliste"
    ]

    selected_program = st.selectbox(
        "Programm auswählen",
        programs,
        key="kl_selected_program"
    )

    # --------------------------------------------------
    # Arbeitsblatt erstellen
    # --------------------------------------------------
    if st.button("AB erstellen", key=f"kl_{selected_program}"):
        if not selected_words:
            st.warning("Bitte zuerst Wörter auswählen!")
        else:
            if selected_program == "Wortschlange":
                word_file = run_Wortschlange(
                    words_with_translations,
                    template_path
                )
            elif selected_program == "Vokabelrätsel":
                word_file = run_Rätsel(
                    words_with_translations,
                    template_path
                )
            elif selected_program == "Vokabelsuchgitter":
                word_file = run_Vokabelsuchgitter(
                    words_with_translations,
                    template_path
                )
            elif selected_program == "Vokabelliste":
                word_file = Vokabellisten(
                    words_with_translations,
                    template_path
                )
            elif selected_program == "Zuordnen":
                word_file = Worte_zuordnen(
                    words_with_translations,
                    template_path
                )

            st.download_button(
                "Word-Datei herunterladen",
                word_file,
                f"{selected_program}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                key="kl_download_word"
            )

    








