import sys, os
from dotenv import load_dotenv
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from agents.annotator_agent import summarize_file
model = os.getenv("MODEL")
root_dir = os.path.dirname(os.path.dirname(__file__))
file_path = os.path.join(root_dir, "repos", "current_repo", "HookData.vb")

print(model)
print("Testing file:", file_path)
print(summarize_file(file_path))
