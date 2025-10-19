import os
import shutil
import subprocess
import requests
from datetime import datetime
from generate_app import create_app
from push_to_github import GITHUB_USERNAME, GITHUB_TOKEN

def handle_round2(data):
    brief = data.get("brief", "Updated app")
    attachments = data.get("attachments", [])
    task_name = data.get("task", "default-task")

    timestamp = data.get('timestamp')
    if not timestamp:
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')

    repo_name = f"{task_name}-{timestamp}"
    repo_path = os.path.join("repo", repo_name)
    os.makedirs(repo_path, exist_ok=True)

    create_app(brief, attachments)
    for file in os.listdir("app"):
        src = os.path.join("app", file)
        dst = os.path.join(repo_path, file)
        if os.path.isdir(src):
            shutil.copytree(src, dst, dirs_exist_ok=True)
        else:
            shutil.copy2(src, dst)

    readme_path = os.path.join(repo_path, "README.md")
    with open(readme_path, "a", encoding="utf-8") as f:
        f.write("\n## Round 2 Update\n")
        f.write(f"Brief changes: {brief}\n")
        f.write(f"Updated at: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}\n")

    if not os.path.exists(os.path.join(repo_path, ".git")):
        subprocess.run(["git", "init"], cwd=repo_path, check=True)
        subprocess.run(["git", "branch", "-M", "main"], cwd=repo_path, check=True)
        subprocess.run([
            "git", "remote", "add", "origin",
            f"https://{GITHUB_USERNAME}:{GITHUB_TOKEN}@github.com/{GITHUB_USERNAME}/{repo_name}.git"
        ], cwd=repo_path, check=True)

    subprocess.run(["git", "add", "."], cwd=repo_path, check=True)
    subprocess.run(["git", "commit", "-m", "Round 2 update"], cwd=repo_path, check=True)
    subprocess.run(["git", "push", "-u", "origin", "main"], cwd=repo_path, check=True)

    commit_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo_path).decode().strip()
    repo_url = f"https://github.com/{GITHUB_USERNAME}/{repo_name}.git"
    pages_url = f"https://{GITHUB_USERNAME}.github.io/{repo_name}/"

    api_url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{repo_name}/pages"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    payload = {"source": {"branch": "main", "path": "/"}}
    response = requests.post(api_url, json=payload, headers=headers)
    if response.status_code in (201, 204):
        print(f"GitHub Pages confirmed at {pages_url}")
    else:
        print(f"Pages re-enable failed: {response.status_code}, {response.text}")

    print(f"Round 2 update completed for {repo_url}")
    return repo_url, pages_url, commit_sha
