# AIrab - Local Research Assistant 


**White or brown-themed PyQt6 desktop app with local Qwen2.5 RAG for Research.**

Upload PDFs → instant intelligent analysis across all files.

## Features

- **Local AI** - Qwen2.5-0.5B (64 tokens/sec CPU inference)
- **Multi-PDF RAG** - Analyzes lectures, papers, ROS docs simultaneously
- **Times New Roman theme** - Clean UI
- **Chat history** - Dummy Password-encrypted persistence
- **File upload** - PDF/TXT (max 3/chat)
- **Zero cloud** - Fully offline after model download


## Quickstart

### **Prerequisites**
- Python 3.12+
- ~400MB disk space (model)

### **1. Clone & Install**
```bash
git clone https://github.com/ali76-AFK/airab.git
cd airab
python -m venv venv
source venv/bin/activate 
pip install -r requirements.txt
```

### **2. Download Model** (~400MB)
```bash
pip install huggingface-hub
huggingface-cli download Qwen/Qwen2.5-0.5B-Instruct-GGUF Qwen2.5-0.5B-Instruct-Q4_K_M.gguf --local-dir models
```

### **3. Two-Terminal Setup**

**Terminal 1** (AI Server - keep running):
```bash
python -m llama_cpp.server \
  --model models/Qwen2.5-0.5B-Instruct-Q4_K_M.gguf \
  --host 0.0.0.0 --port 8080 \
  --n_ctx 2048 --n_threads 4
```

**Terminal 2** (GUI):
```bash
python airab.py
```


## Project Structure

```
airab/
├── src/
│   ├── main_window.py     # PyQt6 brown GUI
│   ├── llm_client.py      # OpenAI-compatible Qwen2.5 client
│   ├── speech.py          # Vosk STT (disabled by default)
│   └── utils.py           # Password encryption + storage
├── models/                # Qwen2.5-0.5B GGUF model
├── AIrab_data/            # Encrypted chat history (gitignored)
└── requirements.txt
```

## Dependencies

| Library | Purpose | Version |
|---------|---------|---------|
| PyQt6 | Beautiful brown GUI | Latest |
| llama-cpp-python | CPU inference server | Latest |
| openai | OpenAI-compatible client | 1.0+ |
| cryptography | Password encryption | Latest |
| keyring | Secure credential storage | Latest |
| PyMuPDF | PDF text extraction | Latest |
| vosk | Speech-to-text | small-en-us |

```bash
pip install PyQt6 llama-cpp-python openai cryptography keyring PyMuPDF vosk
```

## Customization

**Theme** (brown Times New Roman): `src/main_window.py` line 350+
**LLM Model**: Replace `models/Qwen2.5-0.5B-Instruct-Q4_K_M.gguf`
**Context**: `--n_ctx 4096` for longer chats

## Performance

- **Inference**: 60-65 tokens/sec (CPU)
- **PDF Processing**: First 2 pages/file (~1KB context)
- **Max Files**: 3/chat (4000 char context limit)
- **RAM**: ~1.5GB (model + GUI)


## Security

- **Password-encrypted** chat history
- **Local-only** inference (localhost:8080)
- **No cloud APIs**
- **Git-ignored** data directory

## Contributing

1. Fork → clone → create feature branch
2. `pip install -r requirements.txt`
3. Test with your 2-terminal setup
4. PR to `main`

## License

MIT - Free for academic/commercial use.

**Made possible by**: PyQt6, llama.cpp, Qwen2.5, vosk-api

***

⭐ **Star if useful for your research!**
