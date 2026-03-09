from openai import OpenAI

def mock_llm(prompt: str, files_text: str = "") -> str:
    return f"🤖 AIrab: Response to '{prompt[:30]}...'"

_client = None

def get_llm_response(prompt: str, files_text: str = "") -> str:
    global _client
    if _client is None:
        try:
            # PORT 80 (your server) NOT 8080!
            _client = OpenAI(base_url="http://localhost/v1", api_key="not-needed")
        except:
            return mock_llm(prompt, files_text)
    
    try:
        messages = [{"role": "user", "content": prompt}]
        resp = _client.chat.completions.create(model="qwen", messages=messages)
        return resp.choices[0].message.content
    except:
        return mock_llm(prompt, files_text)
