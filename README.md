# Groups Steps Generator

Streamlit app that reproduces the workflow from `Groups_Steps.ipynb` and generates:

- `New_Group_Definitions.xlsx`
- `New_Group_Assignments.xlsx`

## Files expected as input

Upload these three Excel files in the app sidebar:

1. `Case - Static 6 - Nonlinear Stage Data.xlsx`
2. `Groups 1 - Definitions.xlsx`
3. `Groups 2 - Assignments.xlsx`

## What the app does

Given a staged construction case and step range:

1. Builds `W_Step_n` group membership from:
   - `Add Structure`
   - `Remove Structure`
2. Creates new group definitions by copying the `All` row template from **Groups 1 - Definitions**.
3. Merges step groups with **Groups 2 - Assignments** to produce new assignments.
4. Lets you download both output Excel files.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Community Cloud

1. Push this repository to GitHub.
2. In Streamlit Community Cloud, create a new app from this repo.
3. Set the main file to `app.py`.
4. Streamlit will install dependencies from `requirements.txt`.

## Notes

- The app reads Excel using:
  - `header=1`
  - `index_col=0`
- The case name must exist in the first column index of the case file.
- The template row `All` must exist in `Groups 1 - Definitions.xlsx`.
