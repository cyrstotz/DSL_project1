import pandas as pd
import os

# Load all sheets from the Excel file
excel_path = "AI_grading_ThermoI_HS23_Teilpunkte_Alle_240314.xlsx"

# Load the Excel file, set header from row 3 (index 2), and skip rows before actual data
all_sheets = pd.read_excel(excel_path, sheet_name=None, header=2, skiprows=[3])


# Output folder
output_dir = "cleaned_ground_truth_by_subproblem"
os.makedirs(output_dir, exist_ok=True)

for sheet_name, df in all_sheets.items():
    print(f"📄 Processing sheet: {sheet_name}")

    # Select relevant columns
    cols_to_keep = [col for col in df.columns if col.startswith('Ges ')]
    cols_to_keep.insert(0, '#1')  # assuming '#1' is the ID column
    df = df[cols_to_keep]

    # Drop empty or non-numeric IDs
    id_col = df.columns[0]
    df = df[df[id_col].notna()]
    df = df[df[id_col].astype(str).str.isnumeric()]

    # Extract and save point columns
    id_column = df.columns[0]
    point_columns = df.columns[1:]

    problem_number = sheet_name[-1]

    for col in point_columns:
        output_df = df[[id_column, col]].copy()
        output_df.columns = ['ID', 'Points']
        problem_letter = col[-2]
        out_filename = f"problem_{problem_number}{problem_letter}.csv".replace(" ", "_")
        output_path = os.path.join(output_dir, out_filename)
        output_df.to_csv(output_path, index=False, header=False)
        print(f"✅ Saved: {output_path}")