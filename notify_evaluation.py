import requests

def notify_evaluation(evaluation_url, payload):
    if not evaluation_url:
        print("No evaluation URL provided, skipping notification.")
        return
    headers = {"Content-Type": "application/json"}
    try:
        r = requests.post(evaluation_url, json=payload, headers=headers)
        if r.status_code == 200:
            print("Evaluation server notified successfully")
        else:
            print(f"Failed to notify evaluation server: {r.status_code}, {r.text}")
    except Exception as e:
        print(f"Error notifying evaluation server: {e}")
