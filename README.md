# ETH Code Clustering Repository

This sub repository contains scripts and workflows for embedding, clustering, and demonstrating how to use the OpenAI API with Azure used in the report for the DSL Project

---

## Repository Contents

### 1. `data` Folder
   Contains `split_by_subproblem` and `split_by_problem` with all data used in the report



### 2. `Folder structure`

├── data
│   ├── split_by_problem
│   │   ├── grades
│   │   ├── latex
│   │   ├── text_embedding_3_large
│   │   ├── MathBERT_embeddings
│   │   └── get_rid_of_duplicates.py
│   │
│   └── split_by_subproblem
│       ├── grades
│       ├── latex
│       ├── natural_language
│       ├── text_embedding_3_large_subproblem
│       ├── MathBERT_embeddings
│       ├── natural_language_embedding_3_large
│       ├── natural_language_latex
│       ├── NL_with_context
│       ├── NL_with_context_and_interpretation
│       ├── NL_with_context_and_interpretation_embedding_3_large
│       ├── NL_with_context_embedding_3_large
│       └── natural_language_latex_embedding_3_large
│ 
│ 
├── PDF_to_NatLan
│   │   ├── JPGs_Latex
│   │   ├── latex_with_context
│   │   ├── PDFs
│   │   ├── demo_pdf_to_NatLan.py
│   │   ├── pages_to_tasks.py
│   │   └── PDF_to_JPG.py     
│
├── README.md
├── environment.yaml
├── embedder_clean_no_key.py
├── final_results.ipynb
└── latex_to_naturalLanguage.py

   - `data`: has all data used in the report (.tex, .json and .csv)
   - `PDF_to_NatLan`: has the files that create from PDF JPG and then in `demo_pdf_to_NatLan`to text and from `pages_to_tasks` we put the text together according to the subquestions.
  

### 3. `Scripts`
   - `embedder_clean_no_key.py`: example API call of OpenAI models for embeddings
   - `final_results.ipynb`: Jupyter notebook for evaluation of all different models tested in the report
   - `latex_to_naturalLanguage.py`: transforms LaTeX files into 
     
### 4. `.gitignore`
   Configured to ignore: `venv/` (virtual environments) , `env` (include credentials of OpenAI) and other system files. 

### 5. `environment.yaml`
   Specs for conda environment. Create and activate using:
   ```bash
   conda env create -f environment.yaml
   conda activate environment
