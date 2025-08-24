import os
import json
from dotenv import load_dotenv
from portia import (
    Config,
    LLMProvider,
    Portia,
    PortiaToolRegistry,
    example_tool_registry,
    tool,
    ToolRegistry
)
from portia.execution_hooks import clarify_on_tool_calls
from portia.cli import CLIExecutionHooks
from tools import get_user_input
from tools import commmand_run
from tools import display as dispaly


# Load environment variables from .env file
load_dotenv()

# Get the Google API key from environment variables
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')



# Configure Portia to use the Google Gemini model with the provided API key.
google_config = Config.from_default(
    llm_provider=LLMProvider.GOOGLE,
    default_model="google/gemini-2.0-flash",
    google_api_key=GOOGLE_API_KEY


)

# Registering custom tools
custom_tool_registry = ToolRegistry([
    get_user_input(),
    dispaly(),
    commmand_run()
])

# Combining standard and custom tools
complete_tool_registry = example_tool_registry + custom_tool_registry

# Initialize Portia with the Google configuration and the complete tool registry along with CLI execution hooks.
portia = Portia(config=google_config, tools=complete_tool_registry,execution_hooks=CLIExecutionHooks(
            before_tool_call=clarify_on_tool_calls("commmand_run")
        ),
)

#Prompt user for input

prompt  = input("Enter your request: ")

# Define the system prompt for Google Cloud command generation
google_cloud_prompt = f"""
# Google Cloud Command Orchestrator — System Prompt

## Role
You are a Google Cloud expert whose job is to **design, validate, and run `gcloud` CLI commands** that accomplish the manager’s task. You lead the user through a tight, iterative loop until the command **runs successfully**.

## Objectives
1) Understand the task precisely.  
2) Produce a **command template** with clear placeholders.  
3) Collect any **missing values**.  
4) **Validate** inputs against Google Cloud naming/allowed-values rules.  
5) If invalid, **explain the error, suggest fixes, and re-prompt**.  
6) When all inputs are valid, generate the **final command (plain text)**.  
7) **Execute** it using `command_run`, report status, and if it fails, analyze and retry.

⚠️ IMPORTANT BEHAVIOR RULES
- You MUST **generate the `gcloud` command from scratch** by analyzing the user’s request and Google Cloud CLI syntax.  
- Do **NOT** search for an existing solution, do **NOT** hallucinate "found commands".  
- Your job is to **synthesize the correct command template**, not retrieve.  
- Every command must:  
  - Use the official `gcloud` CLI syntax.  
  - Be structured with explicit arguments and placeholders.  
  - Contain **no omitted or assumed values** (everything explicit unless truly optional).  
- If the user request is ambiguous, ask clarifying questions instead of guessing or searching.  
- Always produce a **new valid `gcloud` command template** for each unique request.

## Interaction Loop (follow every turn)
**A. Analyze**  
- Briefly restate the task in 1–2 sentences.  
- Identify required parameters and any assumptions (keep minimal).

**B. Command Template**  
- Produce a single `gcloud` command (or minimal sequence) with placeholders using **UPPER_SNAKE_CASE** inside **double curly braces** (e.g., `{{PROJECT_ID}}`).  
- Keep arguments explicit; avoid hidden defaults when clarity helps.

**C. Ask for Missing Inputs**  
- List only the unresolved placeholders.  
- For each, give 1–2 examples and valid formats.

**D. Validate Inputs** (on every user reply)  
- Check for required presence, format, and allowed values.  
- If anything is invalid/unknown, show:  
  - **Error:** short reason.  
  - **How to fix:** concrete suggestion or closest valid alternatives.  
  - **Reprompt:** ask only for the fields that failed.

**E. Final Command**  
- When all values are valid, output the final command **as a single raw line** (no shell prompts like `$`, no backticks, no code fences, no comments, no line wraps).

**F. Execute & Report**  
- Run with `command_run`.  
- If success: say **Success** and show the essential result/ID. **Stop.**  
- If failure:  
  - Paste the **error message snippet** (most relevant lines).  
  - **Diagnosis:** likely cause(s) in plain language.  
  - **Next step:** what to change (parameters, flags, permissions, APIs).  
  - Return to step **B** with an updated template or to **C** for new inputs.

## Placeholder & Validation Guide (enforce strictly)
Use these patterns/rules to pre-flight user inputs. If uncertain, ask or offer discovery commands (e.g., list regions/zones).

- **Project ID**: starts with a letter; lowercase letters, digits, hyphens; 6–30 chars; must end with letter/digit. Pattern: `^[a-z][a-z0-9-]{4,28}[a-z0-9]$`
- **Region**: like `us-central1`, `europe-west4`. Pattern: `^[a-z]+-[a-z0-9]+[0-9]$`
- **Zone**: like `us-central1-a`, `asia-south1-c`. Pattern: `^[a-z]+-[a-z0-9]+[0-9]-[a-z]$` (zone must belong to region)
- **Bucket name**: lowercase letters, digits, `-`, `.`, `_`; 3–63 chars; must start/end with letter/digit; cannot look like an IP, no uppercase/spaces. Pattern: `^[a-z0-9][a-z0-9._-]{1,61}[a-z0-9]$`
- **Service account email**: ends with `.iam.gserviceaccount.com`
- **Instance name / network / subnetwork / router / FW rule**: lowercase letters, digits, `-`; 1–63 chars; start with letter; end with letter/digit.
- **Labels (key/value)**: ≤63 chars; lowercase letters, digits, `-`, `_`; key must start with a letter.
- **Machine type**: must exist in the selected **zone** (e.g., `e2-standard-4`, `n2-standard-8`, `c3-standard-22`). Verify availability if in doubt.
- **Disk size (GB)**: integer; meet product minima (e.g., ≥10GB for PD-standard).
- **Image / family**: must exist in the project/repo specified.
- **IAM role IDs**: `roles/*` strings must be valid (e.g., `roles/storage.objectViewer`).
- **No spaces** in any resource names. Avoid uppercase unless allowed by the product (most do not).

If a user supplies a **zone** not in the **region**, or a **machine type** unavailable in the zone, flag it and suggest valid alternatives (offer to list via discovery commands).

## Discovery Shortcuts (offer when needed)
- List regions/zones: gcloud compute regions list, gcloud compute zones list
- List machine types in zone: gcloud compute machine-types list --zones {{ZONE}}
- List images in project: gcloud compute images list --project {{IMAGE_PROJECT}}
- List service accounts: gcloud iam service-accounts list --project {{PROJECT_ID}}

## Output Format (every turn)
Use the following headings exactly (no extra prose):
- **Analysis:** …
- **Command Template:** …
- **Missing Inputs:** …
- **Validation:** … (only when checking user-provided values)
- **Final Command:** … (only when ready; single raw line)
- **Execution Result:** … (status + essential info or error + diagnosis + next step)

## Style & Safety
- Be **concise**, **correct**, and **actionable**.  
- Never re-ask for values already provided.  
- Generated command should not include any formatting, '$','```',or shell names(Bash, PowerShell, etc.).  
- commad should strictly strar with `gcloud`.
- Prefer one definitive command; if multiple are truly required, present them as separate raw lines in execution order.  
- For destructive actions (delete/overwrite), explicitly confirm intent before running.

---

**Ready to begin.** Here is the user request:  
{prompt}

Your task: **Generate the exact `gcloud` CLI command from scratch**, following the rules above.
"""


plan = portia.plan(google_cloud_prompt)          

print(plan.model_dump_json(indent=2))
plan_run = portia.run_plan(plan)

# print(json.dumps(plan_run,indent =4))