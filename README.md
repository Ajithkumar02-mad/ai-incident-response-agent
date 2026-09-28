# Incident Response Agent

An AI-powered incident response assistant that uses **Hindsight memory** to recall previous production incidents, successful fixes, and failed fixes before recommending how to respond to a new alert.

The goal is simple:

> **Don't troubleshoot every incident from zero. Learn from what the team already experienced.**

## 1. Problem

When a production incident happens, an on-call engineer often needs to answer:

- Have we seen this problem before?
- What caused it last time?
- Which fix actually worked?
- Which attempted fixes failed?
- What should we try first?

A generic LLM can provide useful troubleshooting advice, but without organizational history it does not automatically know what the team has already experienced.

## 2. Solution

The Incident Response Agent combines:

- **Streamlit** for the user interface
- **Groq** for LLM-based diagnosis
- **Hindsight** for persistent incident memory
- A realistic incident history containing symptoms, root causes, fixes, and outcomes

For each alert, the application provides two views:

### Without memory

The LLM receives only the current alert and produces a baseline diagnosis.

### With memory

The application first recalls relevant memories from Hindsight and gives those memories to the LLM as incident context.

The user can then record whether a proposed fix **worked** or **failed**. That outcome is stored back in Hindsight and can influence future diagnoses.

## 3. Core Workflow

The complete system works as a continuous incident-learning loop:

```text
                    ┌───────────────────┐
                    │   Streamlit UI    │
                    └─────────┬─────────┘
                              │
                         Incident Alert
                              │
                ┌─────────────┴─────────────┐
                │                           │
                ▼                           ▼
        WITHOUT MEMORY                WITH MEMORY
                │                           │
                │                     Hindsight
                │                           │
                │                    Recall relevant
                │                       history
                │                           │
                │                ┌──────────┼─────────┐
                │                │          │         │
                │                ▼          ▼         ▼
                │             Incidents  Worked    Failed
                │                        fixes      fixes
                │                │          │         │
                └────────────────┴──────────┴─────────┘
                                      │
                                      ▼
                                     LLM
                                      │
                                      ▼
                              Diagnosis + Fix
                                      │
                                      ▼
                               Engineer tries
                                    fix
                                      │
                              ┌───────┴───────┐
                              ▼               ▼
                           WORKED           FAILED
                              │               │
                              └───────┬───────┘
                                      ▼
                                  Hindsight
                                      │
                                      ▼
                              Future incidents
                                      │
                                      ▼
                             Better decisions
```

### How to read the architecture

1. **Streamlit UI** receives a production incident alert.
2. The alert is evaluated in two ways:
   - **Without Memory** — the LLM receives the current alert without historical incident context.
   - **With Memory** — Hindsight recalls relevant organizational experience.
3. Hindsight can recall:
   - previous incidents
   - fixes that worked
   - fixes that failed
4. The recalled context is provided to the **LLM**.
5. The LLM produces a diagnosis and ordered troubleshooting steps.
6. The engineer tries a fix in the incident workflow.
7. The engineer records whether the fix **worked** or **failed**.
8. That outcome is stored back in **Hindsight**.
9. A future similar incident can recall the new experience and make a better-informed recommendation.

This feedback loop is the central memory-driven behavior of the project.

## 4. Why Hindsight Matters

Hindsight is central to the application's value.

The memory contains operational experience such as:

```text
Incident:
payments-api returned 504 errors.

Root cause:
Postgres connection pool exhaustion and a
connection leak in the refund handler.

Successful resolution:
Increase max_connections and patch the
refund handler.
```

The agent can also remember failed attempts:

```text
Fix:
Temporarily increased payment worker concurrency to 64.

Outcome:
FAILED.

Future behavior:
Do not recommend this fix for similar alerts.
```

This creates a learning loop:

```text
Incident
   ↓
Recall previous experience
   ↓
Diagnosis
   ↓
Fix attempt
   ↓
Worked / Failed
   ↓
Store outcome in Hindsight
   ↓
Better context for the next incident
```

## 5. Example

### Alert

```text
payments-api is timing out and returning 504 errors
```

### Without memory

The agent may identify a generic upstream dependency or resource problem and suggest checking downstream services, gateway settings, or application capacity.

### With memory

Hindsight can recall previous payments-api incidents involving:

- Postgres connection pool exhaustion
- A refund-handler connection leak
- A successful increase of `max_connections`
- Failed approaches such as increasing the load-balancer timeout
- Failed fixes recorded through the application's feedback loop

The memory-aware diagnosis can therefore prioritize fixes that previously worked and avoid fixes that previously failed.

## 6. Incident Scenarios

The application includes realistic incident history covering multiple services.

### Payments API

504 gateway timeouts, database connection pool exhaustion, slow queries, connection leaks, and deployment-related failures.

### Checkout

502 errors related to Redis failover and stale connection strings.

### Authentication

Login failures, JWT configuration problems, session/Redis issues, and related authentication incidents.

### Inventory / Kafka

Consumer lag, rebalance problems, and slow downstream warehouse API calls.

### Search API

Latency spikes caused by Elasticsearch heap exhaustion and related index/mapping incidents.

### Other services

The incident dataset also contains examples involving:

- notification-service
- order-service
- api-gateway
- user-service
- CoreDNS
- data-pipeline

## 7. Learning From Outcomes

The **Close the loop** section allows the engineer to record the actual result of a fix.

### Fix worked

The agent stores a memory indicating that the fix worked and should be considered for similar alerts.

### Fix failed

The agent stores a memory indicating that the fix failed and should not be recommended for similar alerts.

Example:

```text
Alert:
payments-api is timing out and returning 504 errors

Fix tried:
Temporarily increased payment worker concurrency to 64

Result:
FAILED
```

On a later similar alert, Hindsight can recall this feedback.

## 8. Technology Stack

| Component | Technology |
|---|---|
| UI | Streamlit |
| LLM | Groq |
| Primary model | `openai/gpt-oss-120b` |
| Backup model | `qwen/qwen3-32b` |
| Memory | Hindsight |
| Language | Python |
| Configuration | python-dotenv |

## 9. Project Structure

```text
incident-agent/
│
├── app.py                  # Streamlit application
├── agent.py                # LLM + Hindsight logic
├── incidents.py            # Realistic incident dataset
├── load_incidents_v2.py    # Loads structured incidents into Hindsight
├── test_memory.py          # Read-only Hindsight recall test
│
├── requirements.txt        # Python dependencies
├── .gitignore              # Files excluded from Git
├── .env                    # Local API credentials (not committed)
└── README.md               # Project documentation
```

## 10. Hindsight Memory Bank

The application uses:

```text
oncall-bank-v2
```

The main memory operations are:

### Recall

```python
with memory_client() as m:
    past = m.recall(
        bank_id=BANK,
        query=alert
    )
```

The application takes the most relevant recalled memories and supplies them to the LLM as context.

### Retain successful/failed outcomes

```python
with memory_client() as m:
    m.retain(
        bank_id=BANK,
        content=text,
        context="fix outcome feedback"
    )
```

### Retain resolved incidents

The application can also store a resolved incident as a production post-mortem containing the service, symptom, root cause, fix, and resolution time.

## 11. Setup

### 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd incident-agent
```

### 2. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks script execution, activate the environment using the appropriate local Python/terminal method for your machine.

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

### 4. Create `.env`

Add:

```env
GROQ_API_KEY=your_groq_api_key
HINDSIGHT_URL=your_hindsight_url
HINDSIGHT_API_KEY=your_hindsight_api_key
```

Do **not** commit `.env` to GitHub.

## 12. Load the Initial Incident History

The structured incident dataset can be loaded into the Hindsight memory bank with:

```powershell
python load_incidents_v2.py
```

Run the loader only when the initial incident dataset needs to be loaded. Avoid repeatedly loading the same dataset because the application already uses the populated memory bank.

## 13. Test Hindsight Recall

Run:

```powershell
python test_memory.py
```

This performs a read-only recall against:

```text
oncall-bank-v2
```

and prints the returned memories.

## 14. Run the Application

Start Streamlit:

```powershell
streamlit run app.py
```

Open the local URL shown by Streamlit, normally:

```text
http://localhost:8501
```

## 15. Recommended Demo Flow

A concise demonstration can follow this sequence:

### Step 1 — Show a new alert

```text
payments-api is timing out and returning 504 errors
```

### Step 2 — Compare the two answers

Show:

```text
WITHOUT MEMORY
```

and:

```text
WITH MEMORY
```

Explain that the first response has no organizational incident history, while the second uses memories recalled from Hindsight.

### Step 3 — Show Hindsight evidence

Open:

```text
Incident log Hindsight recalled
```

and show previous incidents and outcome memories.

### Step 4 — Close the loop

Enter a real attempted fix and select:

```text
Fix worked
```

or:

```text
Fix failed
```

### Step 5 — Repeat the alert

Run the same or a similar alert again and show how the stored outcome can influence the recommendation.

## 16. Current Limitations

This prototype uses synthetic but realistic incident data rather than a live production monitoring system.

The application is designed to demonstrate the incident-response workflow and the role of persistent memory. It does not automatically execute infrastructure changes.

The LLM's diagnosis is still probabilistic, so engineers should verify recommendations against the actual production environment before taking operational action.

## 17. Future Extensions

Possible future improvements include:

- Integration with real alerting systems
- Slack or incident-management integrations
- Automatic log and metric retrieval
- Runbook linking
- Incident severity classification
- Role-based access
- Audit history
- Production deployment
- More structured memory metadata and source references

## 18. Key Idea

The core idea is not simply:

```text
AI → answer
```

It is:

```text
AI
 +
Team memory
 +
Past outcomes
 =
Context-aware incident response
```

The agent becomes more useful because it can use what the team has already learned instead of treating every incident as completely new.
