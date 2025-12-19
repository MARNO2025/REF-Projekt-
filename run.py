import os
import sys

script_path = r"C:\Users\phili\Documents\REF-Projekt\app.py"

# Startet Streamlit in einem neuen CMD-Fenster
os.system(f'start cmd /k "{sys.executable} -m streamlit run "{script_path}""')
