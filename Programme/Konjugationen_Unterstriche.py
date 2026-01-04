from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from io import BytesIO
import random


def run_Unterstriche_Konjugationen(
    words_data,
    num_rows,
    selected_time_1,
    selected_time_2,
    template_path
):
    dokument = Document(template_path)

    # =========================
    # Überschrift
    # =========================
    ueberschrift = dokument.add_heading('Test de conjugaison', level=0)
    run = ueberschrift.runs[0]
    run.bold = True
    run.font.size = Pt(18)
    run.font.name = 'Arial'
    ueberschrift.alignment = WD_ALIGN_PARAGRAPH.CENTER
    dokument.add_paragraph('')

    # =========================
    # Hilfsfunktionen
    # =========================
    def set_zeilenhoehe(row, height_cm):
        tr = row._tr
        trPr = tr.get_or_add_trPr()
        trHeight = OxmlElement('w:trHeight')
        trHeight.set(qn('w:val'), str(int(height_cm * 567)))
        trHeight.set(qn('w:hRule'), 'atLeast')
        trPr.append(trHeight)

    def underline_form_with_pronoun(pronoun, form):
        parts = form.split()
        underlined = "   ".join(["_ " * len(part) for part in parts]).strip()
        return f"{pronoun} {underlined}"

    def set_spaltenbreiten(table, widths):
        table.autofit = False
        for row in table.rows:
            for i, width in enumerate(widths):
                row.cells[i].width = width

    def create_table(mode="underline"):
        """
        mode:
        - "underline" → Pronomen + Unterstriche
        - "pronoun"   → nur Pronomen
        """
        table = dokument.add_table(rows=1, cols=4)
        table.style = 'Tabellenraster'
        table.autofit = False

        headers = ["Verbe", selected_time_1, selected_time_2, "En allemand"]
        for i, h in enumerate(headers):
            cell = table.rows[0].cells[i]
            cell.text = h
            para = cell.paragraphs[0]
            para.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = para.runs[0]
            run.bold = True
            run.font.size = Pt(12)

        for entry in exercises:
            row = table.add_row().cells
            row[0].text = entry["verb"]

            if mode == "underline":
                row[1].text = underline_form_with_pronoun(entry["p1"], entry["f1"])
                row[2].text = underline_form_with_pronoun(entry["p2"], entry["f2"])
            elif mode == "pronoun":
                row[1].text = entry["p1"]
                row[2].text = entry["p2"]

            row[3].text = ""

        widths = [Cm(3), Cm(5.522), Cm(5.522), Cm(4)]
        set_spaltenbreiten(table, widths)

        for row in table.rows:
            set_zeilenhoehe(row, 1)

        return table

    # =========================
    # Aufgaben EINMAL erzeugen
    # =========================
    personalpronomen = ["je", "tu", "il", "elle", "on", "nous", "vous", "ils", "elles"]
    infinitives = list(words_data.keys())

    exercises = []

    for _ in range(num_rows):
        verb = random.choice(infinitives)

        p1 = random.choice(personalpronomen)
        f1 = words_data[verb].get(selected_time_1, {}).get(p1, verb)

        p2 = random.choice(personalpronomen)
        f2 = words_data[verb].get(selected_time_2, {}).get(p2, verb)

        exercises.append({
            "verb": verb,
            "p1": p1,
            "f1": f1,
            "p2": p2,
            "f2": f2
        })

    # =========================
    # Seite 1: Unterstriche
    # =========================
    create_table(mode="underline")

    # =========================
    # Seitenumbruch
    # =========================
    dokument.add_page_break()

    # Überschrift Seite 2
    u2 = dokument.add_heading('Test de conjugasion', level=0)
    u2.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # =========================
    # Seite 2: nur Pronomen
    # =========================
    create_table(mode="pronoun")

    # =========================
    # Dokument zurückgeben
    # =========================
    word_stream = BytesIO()
    dokument.save(word_stream)
    word_stream.seek(0)
    return word_stream
