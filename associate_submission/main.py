from agent import run_agent

if __name__ == "__main__":
    print("SunGrid Copilot. Type 'quit' to exit.")
    while True:
        q = input("\nYou: ").strip()
        if q.lower() in ("quit", "exit"):
            break
        print("\nCopilot:", run_agent(q))
