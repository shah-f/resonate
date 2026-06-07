import modal

# Reuse the same image as the deployed app by importing it
from resonate_tribe_modal import image, app


@app.function(image=image, secrets=[modal.Secret.from_name("huggingface-token")], timeout=600)
def debug():
    import os
    # 1. Show the source around the failure point
    src_path = "/usr/local/lib/python3.11/site-packages/neuralset/extractors/text.py"
    with open(src_path) as f:
        lines = f.readlines()
    print("=== text.py lines 290-360 ===")
    for i in range(289, min(360, len(lines))):
        print(f"{i+1:4d} {lines[i]}", end="")

    print("\n=== HF_HOME ===", os.environ.get("HF_HOME"))
    print("=== HF_TOKEN set? ===", bool(os.environ.get("HF_TOKEN")))

    # 2. List what's actually in the HF cache
    hf_home = os.environ.get("HF_HOME", "/root/.cache/huggingface")
    print(f"\n=== contents of {hf_home} ===")
    for root, dirs, files in os.walk(hf_home):
        depth = root.replace(hf_home, "").count("/")
        if depth <= 3:
            print(root)


@app.local_entrypoint()
def dbg():
    debug.remote()
