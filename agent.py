import os
import time
from dotenv import load_dotenv
from groq import Groq
from hindsight_client import Hindsight

load_dotenv()
BANK = "oncall-bank-v2"

llm = Groq(api_key=os.environ["GROQ_API_KEY"], timeout=60.0, max_retries=2)
MODELS = ["openai/gpt-oss-120b", "qwen/qwen3-32b"]  # backup if the first fails


def memory_client():
    return Hindsight(
        base_url=os.environ["HINDSIGHT_URL"],
        api_key=os.environ["HINDSIGHT_API_KEY"],
    )


def ask_llm(prompt: str) -> str:
    """Try each model a few times before giving up."""
    last_error = None
    for model in MODELS:
        for attempt in range(3):
            try:
                r = llm.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                )
                return r.choices[0].message.content
            except Exception as e:
                last_error = e
                time.sleep(2 * (attempt + 1))
    return f"[Could not reach the AI model after several tries: {last_error}]"


def diagnose(alert: str, use_memory: bool = True) -> str:
    past_text = ""
    if use_memory:
        try:
            with memory_client() as m:
                past = m.recall(bank_id=BANK, query=alert)
                past_text = "\n".join(f"- {r.text}" for r in past.results[:12])
        except Exception as e:
            past_text = ""
            print(f"(Memory lookup failed: {e})")

    prompt = f"""You are an on-call incident response assistant.

New alert: {alert}

Past incidents from memory:
{past_text or "None available."}

Rules:
- Answer in at most 7 lines.
- Line 1: most likely root cause.
- Line 2: which past incident it matches (or "no match").
- Then 2-3 fix steps, ordered most likely to work first.
- If a past incident says a fix FAILED or DID NOT WORK, do NOT recommend
  it as a step. Put it on a final line starting with "Avoid:".
- If a past fix WORKED, prefer it and say so.
- Use ONLY facts from the past incidents above. Never invent statistics.
- Only mention table or column names that appear in the past incidents."""

    return ask_llm(prompt)


def record_outcome(alert: str, fix_tried: str, worked: bool):
    if worked:
        text = (f"For the alert '{alert}', the fix '{fix_tried}' WORKED and resolved the problem. "
                f"Recommend this fix for similar alerts.")
    else:
        text = (f"For the alert '{alert}', the fix '{fix_tried}' FAILED and did NOT resolve the problem. "
                f"Do not recommend '{fix_tried}' for similar alerts.")
    with memory_client() as m:
        m.retain(bank_id=BANK, content=text, context="fix outcome feedback")

def record_incident(service: str, symptom: str, root_cause: str, fix: str, minutes: int):
    from datetime import datetime, timezone
    text = (f"Incident on {service}: {symptom}. Root cause: {root_cause}. "
            f"Fix: {fix}. Resolved in {minutes} minutes.")
    with memory_client() as m:
        m.retain(
            bank_id=BANK,
            content=text,
            context="production incident post-mortem",
            timestamp=datetime.now(timezone.utc).isoformat(),
        )


if __name__ == "__main__":
    alert = input("Paste an alert: ")
    print("\n--- WITHOUT MEMORY ---")
    print(diagnose(alert, use_memory=False))
    print("\n--- WITH MEMORY ---")
    print(diagnose(alert, use_memory=True))

    fix = input("\nWhat fix did you try? ")
    worked = input("Did it work? (y/n): ").lower() == "y"
    record_outcome(alert, fix, worked)
    print("Outcome saved to memory.")

    