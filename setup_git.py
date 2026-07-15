"""Initialize git repo and create first commit using dulwich."""
import os, sys
from pathlib import Path
from dulwich.repo import Repo
from dulwich.porcelain import add, commit, status

project_dir = Path(r"C:\Users\admin\Desktop\MarkdownReader")
os.chdir(str(project_dir))

# Initialize repo
try:
    repo = Repo(str(project_dir))
    print("Repo already initialized")
except Exception:
    repo = Repo.init(str(project_dir))
    print("Repo initialized")

# Configure git user
from dulwich.config import ConfigFile
config_path = project_dir / ".git" / "config"
config = ConfigFile.from_path(str(config_path))
config.set(b"user", b"name", b"Jatt9520")
config.set(b"user", b"email", b"jatt9520@users.noreply.github.com")
config.write_to_path(str(config_path))

# Stage all files
print("Staging files...")
add(repo, paths=["."])

# Check status
st = status(repo)
add_count = len(st.staged.get("add", []))
mod_count = len(st.staged.get("modify", []))
del_count = len(st.staged.get("delete", []))
print(f"Staged: {add_count} new, {mod_count} modified, {del_count} deleted")

# Commit
print("Creating commit...")
commit(repo, message=b"Initial commit: MarkdownReader v0.2.0")
print("Commit created!")

head = repo.head()
print(f"HEAD: {head.decode()}")
