"""
Agent CLI – terminal interface to the same agent kernel (Path 3).
Run from backend dir: python -m app.agent_cli [--workspace PATH]
Uses OPENAI_API_KEY or ANTHROPIC_API_KEY from env; no server or auth required.
"""
import argparse
import os
import sys

# Ensure app is importable when run as python -m app.agent_cli from backend
if __name__ == "__main__" and os.path.dirname(os.path.abspath(__file__)) not in sys.path:
    _backend = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if _backend not in sys.path:
        sys.path.insert(0, _backend)

from app.services.agent_kernel import run_loop, execute_pending_and_continue

PENDING_APPROVAL_KEY = "__pending_approval__"


def main() -> None:
    parser = argparse.ArgumentParser(description="Chat with the agent in the terminal (same kernel as web).")
    parser.add_argument(
        "--workspace",
        "-w",
        default=os.environ.get("WORKSPACE_ROOT", ""),
        help="Workspace root path (or set WORKSPACE_ROOT). File tools use this.",
    )
    parser.add_argument(
        "--autonomous",
        "-a",
        action="store_true",
        help="Run edit_file and run_terminal without asking for approval.",
    )
    parser.add_argument(
        "--no-search-context",
        action="store_true",
        help="Disable injecting workspace search context into the agent prompt.",
    )
    parser.add_argument(
        "--agent-style",
        choices=["default", "opus_like"],
        default="default",
        help="Agent style: 'opus_like' = reasoning-first, strict JSON (see docs/OPUS_LIKE_AGENT.md).",
    )
    args = parser.parse_args()

    context = {"workspace_root": args.workspace.strip() or None}
    if context["workspace_root"]:
        if not os.path.isdir(context["workspace_root"]):
            print(f"Error: workspace is not a directory: {context['workspace_root']}", file=sys.stderr)
            sys.exit(1)
        print(f"Workspace: {context['workspace_root']}", file=sys.stderr)
    else:
        print("No workspace set (file tools will fail). Set --workspace or WORKSPACE_ROOT.", file=sys.stderr)

    if args.autonomous:
        context["autonomous"] = True
        print("Autonomous mode: edits and commands run without approval.", file=sys.stderr)
    if args.no_search_context:
        context["inject_search_context"] = False
    if args.agent_style == "opus_like":
        context["agent_style"] = "opus_like"
        print("Agent style: opus_like (reasoning-first, strict JSON).", file=sys.stderr)

    messages: list = []
    print("\nAgent CLI (same kernel as web). Type a message and press Enter. Empty line to exit.\n", file=sys.stderr)

    while True:
        try:
            line = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye.", file=sys.stderr)
            break
        if not line:
            break

        messages.append({"role": "user", "content": line})
        updated, reply, pending, error_code = run_loop(messages=messages, context=context, max_turns=8)
        if error_code:
            print(f"\nAgent error ({error_code}): {reply}\n", file=sys.stderr)
            messages = updated
            continue

        if pending and not context.get("autonomous"):
            tool = pending.get("tool", "?")
            preview = (pending.get("preview") or "")[: 800]
            print(f"\n--- Agent wants to run: {tool} ---\n{preview}\n---", file=sys.stderr)
            try:
                choice = input("Approve? [y/N]: ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                choice = "n"
            if choice == "y" or choice == "yes":
                updated, reply, pending = execute_pending_and_continue(
                    messages=updated,
                    context=context,
                    approved_tool=pending.get("tool", ""),
                    approved_args=pending.get("args") or {},
                    max_turns_after=5,
                )
                messages = updated
                if reply:
                    print(f"\nAgent: {reply}\n")
            else:
                messages = updated + [{"role": "system", "content": "User declined the tool call."}]
                updated2, reply, _, _ = run_loop(messages=messages, context=context, max_turns=3)
                messages = updated2
                if reply:
                    print(f"\nAgent: {reply}\n")
            continue

        messages = updated
        if reply:
            print(f"\nAgent: {reply}\n")
        elif pending:
            print("\n(Pending approval; use --autonomous to run without prompting.)\n", file=sys.stderr)


if __name__ == "__main__":
    main()
