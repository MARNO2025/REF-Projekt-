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

# -----------------------------
# Basis-Pfade
# -----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
template_path = os.path.join(BASE_DIR, "Vorlagen", "Vorlage Vokabellisten.docx")
vokabel_folder = os.path.join(BASE_DIR, "Vokabeln")
kontext_folder = os.path.join(BASE_DIR, "Kontexte")
vocab_folder = os.path.join(vokabel_folder, "vocabs_all")
words_data = os.path.join(BASE_DIR, "unregelmäßige Verben alle")

# Prüfen, ob Ordner existieren
os.makedirs(vocab_folder, exist_ok=True)
os.makedirs(kontext_folder, exist_ok=True)

# Lade alle Vokabeldateien
vocab_files = [f for f in os.listdir(vocab_folder) if f.endswith(".json")]

# -----------------------------
# Hilfsfunktion
# -----------------------------
def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# -----------------------------
# Streamlit Setup
# -----------------------------
st.title("Bonjour")
tab_diff, tab_verben, tab_vokabeln, tab_kontexte, tab_kontexteundLernstand = st.tabs([
    "Differenzierungsmöglichkeiten", "wichtige Verben", "Vokabeln", "Kontexte", "Kontexte & Lernstand"
])

# ========================
# 1️⃣ Differenzierungsmöglichkeiten
# ========================
with tab_diff:
    st.header("Differenzierungsmöglichkeiten")
    user_text = st.text_area(
        "Trag deinen Text ein (Wörter in [Klammern] markieren)",
        height=200,
        key="diff_user_text"
    )

    # Automatisch erstes Wörterbuch laden
    vocab_json = []
    if vocab_files:
        vocab_path = os.path.join(vocab_folder, vocab_files[0])
        vocab_json = load_json(vocab_path)
    else:
        st.warning("Keine Vokabel-Dateien gefunden!")

    if user_text.strip() and vocab_json:
        if st.button("Arbeitsblatt erstellen", key="diff_create_worksheet"):
            st.success("Arbeitsblatt wird erstellt…")
            selected_modules = [1, 2, 3]

            file = generate_worksheets_streamlit(
                text=user_text,
                vocab_json=vocab_json,
                output_prefix="Differenzierung",
                selected_modules=selected_modules,
                template_path=template_path
            )

            st.subheader("Arbeitsblatt zum Download")
            st.download_button(
                label="⬇️ Arbeitsblatt herunterladen",
                data=file,
                file_name="Differenzierung.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                key="diff_download"
            )

# ========================
# 2️⃣ Wichtige Verben
# ========================
with tab_verben:

    # 1️⃣ Basisverzeichnis der JSON-Dateien
    BASE_DIR_Konjugationen_alle = os.path.join(BASE_DIR, "unregelmäßige Verben alle")
    json_files_verbs_alle = [f for f in os.listdir(BASE_DIR_Konjugationen_alle) if f.endswith(".json")]

    if not json_files_verbs_alle:
        st.warning("Keine Verb-Dateien gefunden!")
    else:
        # 2️⃣ Alle JSON-Dateien laden und zu einem Dictionary zusammenführen
        words_data = {}
        for file_name in json_files_verbs_alle:
            json_path = os.path.join(BASE_DIR_Konjugationen_alle, file_name)
            verb_data = load_json(json_path)  # Jede Datei enthält nur ein Verb
            words_data.update(verb_data)      # Fügt das Verb ins Gesamt-Dictionary ein

        st.subheader(f"Arbeitsblatt für {len(words_data)} Verben - Konjugationen mit Unterstrichen")

        # 3️⃣ Anzahl Zeilen für das Arbeitsblatt
        num_rows = st.number_input(
            "Anzahl der Zeilen:",
            min_value=1,
            max_value=100,
            value=20,
            key="verbs_num_rows_underline"
        )

        # 4️⃣ Multiselect für Verben
        all_verbs = list(words_data.keys())
        selected_verbs = st.multiselect(
            "Welche Verben sollen auf dem Arbeitsblatt erscheinen?",
            options=all_verbs,
            default=all_verbs
        )

        # 5️⃣ Auswahl der Zeitformen (nur anzeigen, wenn mindestens ein Verb ausgewählt)
        if selected_verbs:
            first_verb_data = words_data[selected_verbs[0]]
            all_times = list(first_verb_data.keys())

            selected_time_1 = st.selectbox(
                "Zeit 1 auswählen:",
                options=all_times,
                index=0,
                key="time1"
            )

            selected_time_2 = st.selectbox(
                "Zeit 2 auswählen:",
                options=all_times,
                index=1 if len(all_times) > 1 else 0,
                key="time2"
            )

        # 6️⃣ Button zum Arbeitsblatt erstellen
        if st.button("Arbeitsblatt mit Unterstrichen erstellen", key="verbs_create_underline_table"):

            if not selected_verbs:
                st.warning("Bitte wähle mindestens ein Verb aus!")
            else:
                # Filter nur die ausgewählten Verben
                filtered_words_data = {verb: words_data[verb] for verb in selected_verbs}

                # Word-Datei generieren
                word_file = run_Unterstriche_Konjugationen(
                    words_data=filtered_words_data,
                    num_rows=num_rows,
                    selected_time_1=selected_time_1,
                    selected_time_2=selected_time_2,
                    template_path=template_path
                )

                # Download-Button für die Word-Datei
                st.download_button(
                    label="Word-Datei herunterladen",
                    data=word_file,
                    file_name="Konjugationen_Unterstriche.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    key="download_underline_table"
                )

# ========================
# 3️⃣ Vokabeln
# ========================
with tab_vokabeln:
    books = [b for b in os.listdir(vokabel_folder) if os.path.isdir(os.path.join(vokabel_folder, b))]
    if not books:
        st.warning("Keine Bücher/Ordner gefunden!")
    else:
        book_tabs = st.tabs(books)

        if "search_results_vokabeln" not in st.session_state:
            st.session_state.search_results_vokabeln = []

        for book_name, tab in zip(books, book_tabs):
            with tab:
                st.subheader(f"Buch: {book_name}")
                chapters_folder = os.path.join(vokabel_folder, book_name)
                chapters = [c for c in os.listdir(chapters_folder) if os.path.isdir(os.path.join(chapters_folder, c))]

                if not chapters:
                    st.warning("Keine Kapitel gefunden!")
                    continue

                selected_chapter = st.selectbox(
                    f"Kapitel auswählen ({book_name})", chapters, key=f"chapter_{book_name}"
                )
                chapter_folder = os.path.join(chapters_folder, selected_chapter)
                files = [f for f in os.listdir(chapter_folder) if f.endswith(".json")]

                if len(files) < 2:
                    st.warning("Mindestens zwei JSON-Dateien pro Kapitel benötigt!")
                    continue

                selected_file_1 = st.selectbox(f"Erste JSON-Datei auswählen ({book_name})", files, key=f"file1_{book_name}_{selected_chapter}")
                selected_file_2 = st.selectbox(f"Zweite JSON-Datei auswählen ({book_name})", files, key=f"file2_{book_name}_{selected_chapter}")
                selected_vocab_file = st.selectbox(f"Wörterbuch auswählen ({book_name})", vocab_files, key=f"vocab_{book_name}_{selected_chapter}")

                data1 = load_json(os.path.join(chapter_folder, selected_file_1))
                data2 = load_json(os.path.join(chapter_folder, selected_file_2))
                vocab_data = load_json(os.path.join(vocab_folder, selected_vocab_file))

                search_term = st.text_input("Suche Wörter im Wörterbuch", key=f"search_vocab_{book_name}_{selected_chapter}")

                if st.button("Hinzufügen", key=f"add_vocab_{book_name}_{selected_chapter}"):
                    if search_term:
                        filtered = [item for item in vocab_data if search_term.lower() in item['word'].lower()]
                        st.session_state.search_results_vokabeln.extend(filtered)
                        # Dubletten entfernen
                        st.session_state.search_results_vokabeln = list({
                            item['word']: item for item in st.session_state.search_results_vokabeln
                        }.values())

                merged_data = data1 + data2 + st.session_state.search_results_vokabeln
                merged_data = [item for item in merged_data if 'word' in item and 'translation' in item]
                unique_data = list({item['word']: item for item in merged_data}.values())

                selected_words = st.multiselect(
                    "Wörter auswählen",
                    [item["word"] for item in unique_data],
                    default=[item["word"] for item in unique_data],
                    key=f"merged_words_{book_name}_{selected_chapter}"
                )

                words_dict = {item["word"]: item["translation"] for item in unique_data}
                words_with_translations = [(word, words_dict[word]) for word in selected_words]

                programs = ["Vokabelsuchgitter", "Vokabelrätsel", "Wortschlange", "Zuordnen", "Vokabelliste"]
                selected_program = st.selectbox(
                    "Programm auswählen",
                    programs,
                    key=f"program_{book_name}_{selected_chapter}"
                )

                if st.button("AB erstellen", key=f"button_{book_name}_{selected_chapter}"):
                    if not selected_words:
                        st.warning("Bitte zuerst Wörter auswählen!")
                    else:
                        st.success(f"{selected_program} wird mit {len(selected_words)} Wörtern aus {book_name} gestartet!")

                        if selected_program == "Wortschlange":
                            word_file = run_Wortschlange(words_with_translations, template_path=template_path)
                        elif selected_program == "Vokabelrätsel":
                            word_file = run_Rätsel(words_with_translations, template_path=template_path)
                        elif selected_program == "Vokabelsuchgitter":
                            word_file = run_Vokabelsuchgitter(words_with_translations, template_path=template_path)
                        elif selected_program == "Vokabelliste":
                            word_file = Vokabellisten(words_with_translations, template_path=template_path)
                        elif selected_program == "Zuordnen":
                            word_file = Worte_zuordnen(words_with_translations, template_path=template_path)

                        st.download_button(
                            label="Word-Datei herunterladen",
                            data=word_file,
                            file_name=f"{selected_program}.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            key=f"download_{book_name}_{selected_chapter}_{selected_program}"
                        )

# ========================
# 4️⃣ Kontexte
# ========================
with tab_kontexte:
    st.header("Kontexte")

    # Session-State für Kontext-Suche
    if "search_results_kontexte" not in st.session_state:
        st.session_state.search_results_kontexte = []

    kontext_files = [f for f in os.listdir(kontext_folder) if f.endswith(".json")]
    if not kontext_files:
        st.warning("Keine Kontext-Dateien gefunden!")
    else:
        selected_kontext_file = st.selectbox(
            "Wähle einen Kontext aus", kontext_files, key="selected_kontext"
        )

        kontext_data = load_json(os.path.join(kontext_folder, selected_kontext_file))

        # 🔍 Suche (identisch zu Vokabeln)
        search_term = st.text_input(
            "Suche Wörter im Wörterbuch",
            key="search_kontext_vocab"
        )

        if st.button("Hinzufügen", key="add_kontext_vocab"):
            if search_term:
                vocab_all_path = os.path.join(vocab_folder, "zusammengeführt.json")
                vocab_all_data = load_json(vocab_all_path)

                filtered = [
                    item for item in vocab_all_data
                    if search_term.lower() in item["word"].lower()
                ]

                st.session_state.search_results_kontexte.extend(filtered)

                # Dubletten entfernen
                st.session_state.search_results_kontexte = list({
                    item["word"]: item
                    for item in st.session_state.search_results_kontexte
                }.values())

        # 🔗 Kontext + Suchergebnisse zusammenführen
        merged_data = kontext_data + st.session_state.search_results_kontexte

        merged_data = [
            item for item in merged_data
            if "word" in item and "translation" in item
        ]

        unique_data = list({
            item["word"]: item
            for item in merged_data
        }.values())

        # ✅ Multiselect wie bei Vokabeln
        selected_words = st.multiselect(
            "Wörter auswählen",
            [item["word"] for item in unique_data],
            default=[item["word"] for item in unique_data],
            key="context_vocab"
        )

        words_dict = {
            item["word"]: item["translation"]
            for item in unique_data
        }

        words_with_translations = [
            (word, words_dict[word]) for word in selected_words
        ]

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
            key="program_kontexte"
        )

        if st.button("AB erstellen", key="run_kontext_program"):
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
                    key="download_kontext"
                )
                
# ========================
# 5️⃣ Kontexte & Lernstand
# ========================

with tab_kontexteundLernstand:
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
        max_value=10,
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
                "zusammengeführt.json"
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
    if st.button("AB erstellen", key="kl_run_program"):
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

    


