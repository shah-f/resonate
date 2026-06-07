import modal

app = modal.App("resonate-test")

@app.function()
def hello():
    return "Modal is working! 🧠"

@app.local_entrypoint()
def main():
    result = hello.remote()
    print(result)
