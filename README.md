# editor_ia

**editor_ia** is a personal project built to revise and improve the readability of Chinese-to-English webnovel translations. The goal here isn’t to rewrite chapters or republish anything — it’s just to make amateur translated or machine translated novels more readable, emotional, and smooth without losing their original tone, names, or structure.

This repo exists because current LLM pipelines aren’t great at this task out of the box — especially when you need something that:
- doesn’t censor plot-relevant content,
- runs on GPU (CUDA),
- is consistent with style and output,
- and doesn't hallucinate or try to "explain" the story.

---

## 🧠 The Model

We use [teknium/OpenHermes-2.5-Mistral-7B](https://huggingface.co/teknium/OpenHermes-2.5-Mistral-7B), which so far has been one of the best uncensored models that:
- runs reliably on a local GPU,
- produces stable, high-quality outputs,
- respects the prompt structure (when properly prepared).

Finding a balance between performance, weight and being uncensored was a headache. Many models either filtered entire blocks, refused to edit “sensitive” text, or added commentary. This one doesn’t — which is why it was chosen.

---

## 📚 Why This Exists

We’re not trying to “refine” a translation into literature — just clean it up enough to read fluently. This means:
- No name changes
- No removing of emotional exaggeration
- No reassigning who said what
- No turning "sword dao" into “ideological martial training” or some nonsense

Only **fixing what breaks immersion**, and leaving the rest as is.

---

## 🔨 Key Features and Design Decisions

### ✅ Block Segmentation
LLMs don’t deal well with giant blobs of text — and full chapters break prompt limits fast. So we split each chapter into **smaller, natural-sounding blocks** using punctuation and line count as boundaries.

This keeps prompts short and coherent, and keeps the model from losing the thread.

### ✅ re.sub Cleanup
Unfortunately, even good models sometimes act like chatbots.  
That means:
- echoing the prompt,
- re-injecting system messages,
- or adding `user:` and `assistant:` tags.

All of that is stripped out with carefully tuned `re.sub()` calls that we tested against real outputs. This wasn’t overkill — it was necessary.

### ✅ Modular Structure
We split the code into clean modules:

- `modelo/`: loads and preps the model/tokenizer

- `processamento/`: handles block segmentation and interaction with the LLM.

- `editor/`: coordinates the docx read/segment/rewrite/save flow

- `dados/entrada/` and `dados/saida/`: clear separation of raw vs processed files

We didn't invent extra functions unless absolutely needed — just separated logic for clarity.

---

## 🚀 How to Use

1. Drop your `.docx` file (a chapter batch) into `dados/entrada/`. 
2. You can adjust the model's temperature, ranging from 0.6 to 0.8 — increasing it makes the editor more likely to introduce creative changes.
3. Run `app.py`
4. The revised version will show up in `dados/saida/`, with `_revisado` added to the filename

⚠️ On first run, the Hugging Face model (`teknium/OpenHermes-2.5-Mistral-7B`) will be downloaded automatically.  
You may need to log in to your Hugging Face account if you haven't configured access before.

You’ll get live progress updates, batch processing logs, and a total time summary at the end.

---

## 📁 Project Structure

```
editor_ia/
├── app.py                  # Run this to start the revision process
├── dados/
│   ├── entrada/            # Drop your original .docx files here
│   └── saida/              # Revised files appear here
├── modelo/
│   └── carregador.py       # Loads tokenizer and model
├── processamento/
│   ├── segmentador.py      # Splits text into manageable blocks
│   ├── revisor_llm.py      # Sends prompts to the model and processes response
│   └── limpador.py         # (optional, for cleanup logic)
├── editor/
│   └── editor_docx.py      # Coordinates docx loading and saving
├── utils/
│   └── constantes.py       # (optional, for shared config/prompt storage)
```


---

## ⏱️ Performance

On an RTX 4080 GPU, the processing time is approximately **3 minutes for every 2200 words**. This can vary depending on:
- how the text gets tokenized,
- how many lines end up in each block,
- and how consistently the model adheres to the prompt instructions.

---

## 🔒 Usage Disclaimer

This is strictly a **personal-use** tool for improving private readability of purchased or archived content.  
We don’t host, share, or re-upload any original or edited material.  
If you're using this, you're expected to respect copyright and usage rights.

---

## ✍️ Built by

Created by **Roman Brocki**, mixing personal expertise with the assistance of **ChatGPT-4o**  
to refine structure, modularize components, and optimize model interaction for speed and reliability.

This project came out of necessity — tested against real chapters, and tuned until it worked the way it should.
