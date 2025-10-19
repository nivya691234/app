import requests
import os
import base64
import json

AIPIPE_TOKEN = os.getenv("AIPIPE_TOKEN")
def create_app(brief, attachments):
    os.makedirs("app", exist_ok=True)
    user_prompt = brief
    prompt = user_prompt + "\n"
    if attachments:
        prompt += "The following attachments are provided (use as app samples if needed):\n"
        for att in attachments:
            prompt += f"- {att['name']} (data URI)\n"

    headers = {
        "Authorization": f"Bearer {AIPIPE_TOKEN}",
        "Content-Type": "application/json"
    }
    llm_payload = {
        "model": "openai/gpt-4.1-nano",
        "messages": [
            {
                "role": "system",
                "content": "You are a code generator. Given a brief, return ONLY a valid JSON object with a top-level key 'files', where each value is the file content for a static web app (index.html, script.js, README.md, etc). Do NOT include any explanation, Markdown, or code blocks. Only output the JSON object, nothing else."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    }
    url = "https://aipipe.org/openrouter/v1/chat/completions"
    response = requests.post(url, json=llm_payload, headers=headers)
    result = response.json()

    print("LLM raw response:", result)  # Debug

    files_json = None
    for choice in result.get("choices", []):
        msg = choice.get("message", {}).get("content", "")
        print("LLM message content:", msg)  # Debug
        try:
            files_json = json.loads(msg)
            print("Parsed JSON directly.")
            break
        except Exception as e:
            print("Direct JSON parsing failed:", e)
            continue

    if not files_json or "files" not in files_json:
        raise Exception("LLM did not return expected files JSON.")

    for filename, content in files_json["files"].items():
        with open(os.path.join("app", filename), "w", encoding="utf-8") as f:
            f.write(content)

    for att in attachments:
        name, dataurl = att['name'], att['url']
        if dataurl.startswith("data:"):
            header, encoded = dataurl.split(",", 1)
            path = os.path.join("app", name)
            with open(path, "wb") as f:
                f.write(base64.b64decode(encoded))
