from openai import OpenAI

def get_llm_response(prompt: str, files_text: str = "") -> str:
    try:
        client = OpenAI(base_url="http://localhost:8080/v1", api_key="not-needed")
        messages = [
            {"role": "system", "content": "You are AIrab, helpful robotics/ML assistant. Use UPLOADED FILES context for answers."},
            {"role": "user", "content": f"{prompt}\n\n=== UPLOADED FILES ===\n{files_text}\n=== END FILES ===\nAnswer using file content."}
        ]
        resp = client.chat.completions.create(model="qwen", messages=messages, max_tokens=512)
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"🤖 AIrab: {prompt[:30]}... (Server: {str(e)[:50]})"
