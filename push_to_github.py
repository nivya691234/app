import os
import shutil
import subprocess
from datetime import datetime
import requests

GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

def create_github_repo(repo_name, private=False):
    api_url = "https://api.github.com/user/repos"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    payload = {"name": repo_name, "private": private, "auto_init": False}
    r = requests.post(api_url, json=payload, headers=headers)
    if r.status_code in (201, 422):
        print(f"GitHub repo '{repo_name}' is ready.")
    else:
        raise Exception(f"Failed to create GitHub repo: {r.status_code}, {r.text}")

def create_repo(task_name, brief, checks):
    repo_name = f"{task_name}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    repo_url = f"https://github.com/{GITHUB_USERNAME}/{repo_name}.git"
    pages_url = f"https://{GITHUB_USERNAME}.github.io/{repo_name}/"

    create_github_repo(repo_name, private=False)
    os.makedirs("repo", exist_ok=True)
    repo_path = os.path.join("repo", repo_name)
    os.makedirs(repo_path, exist_ok=True)

    # Copy files from app dir
    for file in os.listdir("app"):
        src = os.path.join("app", file)
        dst = os.path.join(repo_path, file)
        if os.path.isdir(src):
            shutil.copytree(src, dst, dirs_exist_ok=True)
        else:
            shutil.copy2(src, dst)

    # README with checks included
    readme_path = os.path.join(repo_path, "README.md")
    with open(readme_path, "a", encoding="utf-8") as f:
        f.write("\n\n## Evaluation criteria (checks):\n")
        for check in checks:
            f.write(f"- {check}\n")

    license_path = os.path.join(repo_path, "LICENSE")
    with open(license_path, "w", encoding="utf-8") as f:
        f.write("MIT License\n\nCopyright (c) 2025\n...")

    # Git workflow
    subprocess.run(["git", "init"], cwd=repo_path, check=True)
    # Set git user config for this repo
    subprocess.run(["git", "config", "user.email", "24f1002781@ds.study.iitm.ac.in"], cwd=repo_path, check=True)
    subprocess.run(["git", "config", "user.name", "nivas68"], cwd=repo_path, check=True)
    subprocess.run(["git", "add", "."], cwd=repo_path, check=True)
    subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=repo_path, check=True)
    subprocess.run(["git", "branch", "-M", "main"], cwd=repo_path, check=True)
    subprocess.run(
        ["git", "remote", "add", "origin", f"https://{GITHUB_USERNAME}:{GITHUB_TOKEN}@github.com/{GITHUB_USERNAME}/{repo_name}.git"],
        cwd=repo_path, check=True
    )
    subprocess.run(["git", "push", "-u", "origin", "main"], cwd=repo_path, check=True)

    commit_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo_path).decode().strip()

    # Enable GitHub Pages
    api_url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{repo_name}/pages"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    payload = {"source": {"branch": "main", "path": "/"}}
    response = requests.post(api_url, json=payload, headers=headers)
    if response.status_code in (201, 204):
        print(f"GitHub Pages enabled at {pages_url}")
    else:
        print(f"Failed to enable Pages: {response.status_code}, {response.text}")

    print(f"Repo created at {repo_url}")
    return repo_url, pages_url, commit_sha
