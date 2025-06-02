from pathlib import Path
import re
from collections import defaultdict

def save_task_tex_files(page_outputs, task_labels, student_id, output_folder):
    output_folder = Path(output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)

    task_contents = {label: [] for label in task_labels}

    # Collect content from each page for each task
    for text in page_outputs:
        for label in task_labels:
            pattern = rf"TASK\s+{label}\s*\n(.*?)(?=(\nTASK\s+\w+)|\Z)"  # match task block
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            if match:
                content = match.group(1).strip()
                if content and content.lower() != "this is empty":
                    task_contents[label].append(content)

    # Write each task to a separate .tex file
    for label in task_labels:
        file_path = output_folder / f"{student_id}_{label}.tex"
        content_list = task_contents[label]
        if content_list:
            final_content = "\n\n".join(content_list)
        else:
            final_content = ""
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(final_content)

    print(f"Generated {len(task_labels)} .tex files for student {student_id} in {output_folder}")

def group_outputs_by_student(tex_folder):
    """
    Reads all .tex files and groups their contents by student ID.
    Returns a dict: {student_id: [list of page texts in order]}
    """
    tex_folder = Path(tex_folder)
    grouped = defaultdict(list)

    for file in sorted(tex_folder.glob("*.tex")):
        match = re.match(r"(\d{3})_(\d+)\.tex", file.name)
        if match:
            student_id, _ = match.groups()
            content = file.read_text(encoding="utf-8")
            grouped[student_id].append(content)
    return grouped

def save_all_students_tex_files(tex_folder, task_labels, output_folder):
    student_outputs = group_outputs_by_student(tex_folder)
    for student_id, page_outputs in student_outputs.items():
        save_task_tex_files(page_outputs, task_labels, student_id, output_folder)

# === Example Usage ===
if __name__ == "__main__":
    task_labels = [
        "1a", "1b", "1c", "1d", "1e",
        "2a", "2b", "2c", "2d",
        "3a", "3b", "3c", "3d",
        "4a", "4b", "4c", "4d", "4e"
    ]

    input_folder = "PDF_to_NatLan/JPGs_Latex"  # folder with page-level .tex files like 002_0.tex
    output_folder = "PDF_to_NatLan/latex_with_context"             # output folder for split task files

    save_all_students_tex_files(input_folder, task_labels, output_folder)
