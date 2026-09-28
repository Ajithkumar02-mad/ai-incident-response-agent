import os
from dotenv import load_dotenv
from hindsight_client import Hindsight
from incidents import INCIDENTS

load_dotenv()
BANK = "oncall-bank-v2"

with Hindsight(
    base_url=os.environ["HINDSIGHT_URL"],
    api_key=os.environ["HINDSIGHT_API_KEY"],
) as client:
    for inc in INCIDENTS:
        try:
            client.retain(
                bank_id=BANK,
                content=inc["text"],
                context="production incident post-mortem",
                timestamp=f"{inc['date']}T10:00:00Z",
                document_id=inc["id"],
            )
            print("Stored", inc["id"], inc["date"])
        except Exception as e:
            print("FAILED", inc["id"], e)

print("Done. Wait 3-5 minutes for Hindsight to finish processing.")