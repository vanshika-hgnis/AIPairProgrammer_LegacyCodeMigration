import subprocess, yaml, os, openai
from datetime import datetime

# 1. Load config
config = yaml.safe_load(open("config.yaml", "r"))
MODEL_NAME = config["model"]["model_name"]
CDIGET = config["paths"]["cdiget_exe"]
OUT_DIR = config["paths"]["output_dir"]
os.makedirs(OUT_DIR, exist_ok=True)


def run_cdiget(path):
    """Run cdiget and capture its text output."""
    result = subprocess.run([CDIGET, path], capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr)
    return result.stdout


def run_inference(code_text, prompt_path="prompts/migration_prompt.txt"):
    """Send the cdiget output to an AI model for analysis."""
    system_prompt = open(prompt_path).read()
    client = openai.OpenAI()
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": code_text[:15000]},  # truncate for safety
        ],
    )
    return response.choices[0].message.content


def main():
    project_path = r"C:\Users\lenovo\Desktop\SoftwareCourses\Reuse\Project\vbnet-whatsapp-chatbot-main"
    print(f"Running cdiget on {project_path}...")
    analysis_text = run_cdiget(project_path)
    analysis_file = os.path.join(OUT_DIR, "vbnet-whatsapp-analysis.txt")
    with open(analysis_file, "w", encoding="utf-8") as f:
        f.write(analysis_text)
    print(f"Analysis saved to {analysis_file}")

    print("Running model inference...")
    insights = run_inference(analysis_text)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    out_file = os.path.join(OUT_DIR, f"inference-{timestamp}.txt")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(insights)
    print(f"AI insights saved to {out_file}\n")
    print(insights)


if __name__ == "__main__":
    main()
