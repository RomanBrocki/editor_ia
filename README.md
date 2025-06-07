# editor_ia

**editor_ia** is a personal project built to revise and improve the readability of Chinese-to-English webnovel translations. The goal isn’t to rewrite chapters — it’s to clean up MTLs or amateur translations so they read smoothly, emotionally, and faithfully to the original structure.

---

## 🧠 The Model

We use [teknium/OpenHermes-2.5-Mistral-7B](https://huggingface.co/teknium/OpenHermes-2.5-Mistral-7B) (or variants like `Hermes-2-Pro-Mistral-7B`) because it:
- runs locally on GPU (CUDA),
- respects prompt structure,
- doesn't censor or hallucinate,
- produces smooth, human-quality edits.

---

## 📚 Why This Exists

This project was built because most machine-translated or amateurishly translated novels:
- have inconsistent chapter structure, often lacking proper paragraphs,
- can’t be trusted to produce clean syntax or coherent flow,
- may filter or mangle “sensitive” content.


So this tool:
- preserves names, exaggerated emotions, pacing and idioms,
- does not reassign dialogue or add text,
- corrects grammar, punctuation, text flow.

---

## 🔨 Key Features

### ✅ Block Segmentation
Each chapter is split into natural-sounding **blocks**, typically 3–7 lines long, ending in punctuation. This avoids prompt overflows and keeps the model focused.

### ✅ Prompt Enforcement
Each prompt uses structured `<|im_start|>` tags to simulate system/user/assistant interaction. The prompt instructs the model not to alter structure or meaning, only to revise fluency and correctness.

### 🧠 Smart Fallback Handling
The review system has been upgraded to handle partial LLM failures intelligently:
Each text block is reviewed individually.
- If the model fails to return a valid response, a second attempt is made only on the failed blocks.
- If the second attempt also fails, the original block is retained.
- This ensures robustness without unnecessary retries.

### ✅ Cleanup
The output is sanitized via `re.sub` to remove chat artifacts:
- system echoes,
- `<|im_x|>` tags,
- assistant commentary,
- “No changes needed.”

### 🧾 Detailed Review Logging
After processing, a .txt log file is created in dados/logs/, including per-chapter details:
- Number of processed blocks;
- Token counts (input and output);
- Time taken for each chapter;
- Count of fallback errors;
- Origin of final text blocks:
    - Revised on 1st try
    - Revised on 2nd try
    - Kept as original

This provides traceability and helps assess both quality and performance.

### 🖥️ Enhanced Terminal Output
The terminal now displays:
- Chapter-by-chapter progress;
- Duration of each chapter’s review after completion.
Example:
[📖] 2/10: Chapter 2002: Death And Darkness
[✅] Completed: Chapter 2002: Death And Darkness (2m 23s)


## 🚀 How to Use

1. Drop your `.docx` file(s) into `dados/entrada/`.
2. Run `app.py` or call `revisar_docx_otimizado()` directly.
3. Find the revised `.docx` in `dados/saida/`.
4. Logs are saved in `dados/logs/`.

You can tweak:
- the model, temperature, prompt in `utils/config.py`.

---

## 📁 Project Structure

editor_ia/
├── app.py
├── dados/
│ ├── entrada/
│ ├── saida/
│ └── logs/
├── modelo/
│ └── carregador.py
├── processamento/
│ ├── segmentador.py
│ ├── revisor_llm.py
├── editor/
│ └── editor_docx.py
├── utils/
│ ├── config.py
│ └── logger.py

---

## ⏱️ Performance

On an RTX 4080:
- Avg 2-3 minutes per chapters
- ~2.500 tokens/chapter

---

## 🔒 Disclaimer

This tool is strictly for **personal use** to improve the readability of legally obtained content.  
No content is hosted, shared or republished.

---

## ✍️ Built by

Created by **Roman Brocki** with modular, efficient processing, live feedback, and local GPU support — tuned for high-volume batch webnovel cleanup.

