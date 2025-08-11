
Mission_99.1_SynHack3.0
=======================

Contents:
- pitch_deck.pptx
- app.py
- data/accounts.csv
- data/transactions.csv
- screenshots/*.png
- demo_script.txt

Run the demo:
1. Install dependencies (recommended to use a virtualenv):
   pip install -r requirements.txt

2. Run:
   streamlit run app.py

Notes:
- transactions.csv is synthetic and safe for demo.
- The app auto-filters suspicious transactions (marked 'suspicious' in the CSV).
