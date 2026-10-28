"""python -m copilot ask "question" [--json]"""
import argparse
import json
from dataclasses import asdict

from copilot.agent import Copilot


def main():
    parser = argparse.ArgumentParser(prog="copilot")
    sub = parser.add_subparsers(dest="command", required=True)
    ask = sub.add_parser("ask", help="ask the copilot one question")
    ask.add_argument("question")
    ask.add_argument("--json", action="store_true", help="print the full result, including retrieval and tool details")
    args = parser.parse_args()

    copilot = Copilot()
    try:
        result = copilot.ask(args.question)
    finally:
        copilot.close()
    if args.json:
        print(json.dumps(asdict(result), indent=2))
        return
    print(result.answer)
    if result.citations:
        print("\nSources: " + ", ".join(result.citations))
    if result.sources_disagree:
        print("(The sources disagree on this point.)")


if __name__ == "__main__":
    main()
