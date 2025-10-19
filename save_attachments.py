import os
import base64

def save_attachments(attachments):
    os.makedirs("attachments", exist_ok=True)
    for att in attachments:
        name = att.get("name")
        url = att.get("url")
        if not name or not url:
            continue
        if url.startswith("data:"):
            try:
                header, encoded = url.split(",", 1)
                path = os.path.join("attachments", name)
                with open(path, "wb") as f:
                    f.write(base64.b64decode(encoded))
                print(f"Saved attachment: {path}")
            except Exception as e:
                print(f"Error saving attachment {name}: {e}")
