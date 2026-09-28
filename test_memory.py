import os
from dotenv import load_dotenv
from hindsight_client import Hindsight

load_dotenv()

BANK = "oncall-bank-v2"

with Hindsight(
    base_url=os.environ["HINDSIGHT_URL"],
    api_key=os.environ["HINDSIGHT_API_KEY"],
) as client:

    result = client.recall(
        bank_id=BANK,
        query="payments-api is timing out and returning 504 errors"
    )

    for memory in result.results[:8]:
        print("-", memory.text)