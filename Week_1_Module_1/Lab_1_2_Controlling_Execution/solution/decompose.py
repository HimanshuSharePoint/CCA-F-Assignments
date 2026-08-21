import json
import anthropic


# ---------------------------------------------------------
# ANTHROPIC CLIENT
# ---------------------------------------------------------

# The client automatically reads ANTHROPIC_API_KEY
# from the Windows environment variable.
client = anthropic.Anthropic()


# ---------------------------------------------------------
# SHARED CLAUDE HELPER
# ---------------------------------------------------------

def ask_claude(
    system,
    user,
    max_tokens=800,
    model="claude-haiku-4-5-20251001"
):
    """
    Makes one Claude API call and returns the text response.
    """

    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system,
        messages=[
            {
                "role": "user",
                "content": user
            }
        ]
    )

    text_parts = []

    for block in response.content:
        if block.type == "text":
            text_parts.append(block.text)

    return "\n".join(text_parts).strip()


# ---------------------------------------------------------
# FIXED DECOMPOSITION
# ---------------------------------------------------------

def run_fixed_intel_digest(
    overnight_feed,
    asset_inventory
):
    """
    Runs the same three steps every time:

    1. Extract indicators of compromise.
    2. Match indicators against NorthGate assets.
    3. Produce an executive brief.
    """

    print("\n" + "=" * 70)
    print("FIXED DECOMPOSITION: MORNING THREAT-INTEL DIGEST")
    print("=" * 70)

    # -----------------------------------------------------
    # FIXED STEP 1: EXTRACT INDICATORS
    # -----------------------------------------------------

    print("\nFixed Step 1: Extracting indicators of compromise...")

    iocs = ask_claude(
        system=(
            "Extract every indicator of compromise as a JSON list "
            "of objects containing type, value, and context. "
            "The type must be one of ip, hash, domain, or cve. "
            "Return ONLY the JSON array. "
            "Do not include Markdown or explanations."
        ),
        user=f"""
Extract all indicators of compromise from this overnight threat feed.

Overnight threat feed:

{overnight_feed}
""",
        max_tokens=800
    )

    print("\nEXTRACTED IOCS:")
    print(iocs)

    # -----------------------------------------------------
    # FIXED STEP 2: ENRICH AND MATCH
    # -----------------------------------------------------

    print("\nFixed Step 2: Matching indicators against assets...")

    matches = ask_claude(
        system=(
            "You are a SOC threat-intelligence enrichment analyst. "
            "Compare the supplied indicators of compromise with the "
            "NorthGate asset inventory. "
            "List every indicator that matches something NorthGate "
            "owns or uses. "
            "Return one clear bullet per match. "
            "Name the indicator, matching asset, and why it matters."
        ),
        user=f"""
Indicators of compromise:

{iocs}

NorthGate asset inventory:

{asset_inventory}
""",
        max_tokens=800
    )

    print("\nMATCHING NORTHGATE ASSETS:")
    print(matches)

    # -----------------------------------------------------
    # FIXED STEP 3: EXECUTIVE BRIEF
    # -----------------------------------------------------

    print("\nFixed Step 3: Creating executive brief...")

    exec_brief = ask_claude(
        system=(
            "You are preparing the 08:00 SOC manager standup. "
            "Write exactly three concise executive bullets. "
            "Each bullet must name the affected asset and recommend "
            "the next action. "
            "Use only the supplied indicators and match results."
        ),
        user=f"""
Indicators of compromise:

{iocs}

NorthGate asset matches:

{matches}
""",
        max_tokens=600
    )

    print("\nEXECUTIVE BRIEF:")
    print(exec_brief)

    return {
        "iocs": iocs,
        "matches": matches,
        "exec_brief": exec_brief
    }


# ---------------------------------------------------------
# ADAPTIVE DECOMPOSITION BRANCHES
# ---------------------------------------------------------

TRIAGE_BRANCHES = {
    "phishing": (
        "You are a phishing-response specialist. "
        "Review email evidence, identify malicious URLs or attachments, "
        "recommend mailbox containment, collect headers, and state when "
        "the incident must be escalated."
    ),

    "malware": (
        "You are a malware-response specialist. "
        "Review endpoint evidence, recommend host containment, collect "
        "process and file indicators, and define escalation criteria."
    ),

    "lateral_movement": (
        "You are a lateral-movement investigation specialist. "
        "Review authentication and network movement, identify affected "
        "hosts and accounts, recommend containment, and define escalation."
    ),

    "data_exfiltration": (
        "You are a data-exfiltration response specialist. "
        "Review transfer activity, identify the source asset and "
        "destination, preserve evidence, recommend containment, and "
        "state when legal and senior SOC leadership must be notified."
    ),

    "brute_force": (
        "You are an identity and brute-force response specialist. "
        "Review failed logins, source addresses, and targeted accounts, "
        "recommend account protection, and state escalation criteria."
    ),

    "false_positive": (
        "You are a SOC false-positive review specialist. "
        "Validate whether the activity is authorized, collect supporting "
        "evidence, document the reason, and recommend closure only when "
        "the evidence clearly supports it."
    )
}


# ---------------------------------------------------------
# ADAPTIVE CLASSIFIER
# ---------------------------------------------------------

def classify_alert(alert_text):
    """
    Classifies an alert into one of six supported branches.
    """

    allowed_labels = list(TRIAGE_BRANCHES.keys())

    classification = ask_claude(
        system=(
            "Classify the security alert into exactly one of these labels: "
            "phishing, malware, lateral_movement, data_exfiltration, "
            "brute_force, false_positive. "
            "Reply with ONLY one label. "
            "Do not add punctuation, explanations, or Markdown."
        ),
        user=f"""
Classify this security alert:

{alert_text}
""",
        max_tokens=50
    )

    label = classification.strip().lower()

    # Remove accidental quotation marks.
    label = label.replace('"', "").replace("'", "")

    if label not in allowed_labels:
        print(
            f"\nWarning: Unknown classifier label '{label}'. "
            "Using false_positive as the lab fallback."
        )

        label = "false_positive"

    return label


# ---------------------------------------------------------
# ADAPTIVE TRIAGE
# ---------------------------------------------------------

def run_adaptive_triage(alert_text):
    """
    Classifies an alert and routes it to one specialist branch.
    """

    print("\nClassifying alert...")

    branch = classify_alert(alert_text)

    print(f"Selected branch: {branch}")

    specialist_prompt = TRIAGE_BRANCHES[branch]

    answer = ask_claude(
        system=(
            specialist_prompt
            + " Produce a concise triage response containing: "
            + "classification rationale, immediate containment, "
            + "evidence to collect, and escalation criteria."
        ),
        user=f"""
Perform specialist triage for this alert:

{alert_text}
""",
        max_tokens=900
    )

    return {
        "branch": branch,
        "answer": answer
    }


# ---------------------------------------------------------
# TEST DATA
# ---------------------------------------------------------

OVERNIGHT_FEED = """
1. Threat researchers observed suspicious outbound traffic to
   IP 203.0.113.47. The address is associated with large data
   transfers from compromised financial-sector endpoints.

2. The domain secure-northgate-login.example was used in a
   credential-phishing campaign targeting financial analysts.

3. A malware sample with SHA-256 hash
   44d88612fea8a8f36de82e1278abb02f
   was reported by two security vendors.

4. CVE-2027-1142 affects the remote-access gateway product
   used by several financial-services organizations.

5. Reuters market-data IP 198.51.100.10 remains legitimate
   and should not be treated as malicious.
"""


ASSET_INVENTORY = """
NorthGate Capital asset inventory:

- research-analyst-laptop-04
  Owner: Maya Iyer
  Department: Equity Research
  Recent destination: 203.0.113.47

- vpn-gateway-prod-01
  Product: Remote access gateway
  Vulnerability tracking: CVE-2027-1142

- email-security-gateway-01
  Monitors domains targeting northgatecapital.com users

- market-data-relay-01
  Approved Reuters IP: 198.51.100.10
"""


DATA_EXFILTRATION_ALERT = """
Alert ID: NG-2027-1142
Severity: HIGH
Source: CrowdStrike Falcon EDR
Time: 02:47 EST
Asset: research-analyst-laptop-04
Owner: Maya Iyer
Event: Outbound transfer of 8.3 GB to external IP 203.0.113.47
Geolocation: Singapore
Context: Transfer occurred outside business hours.
No active VPN session was present.
The owner's badge record shows departure at 18:22 EST.
"""


PHISHING_ALERT = """
Alert ID: NG-2027-1201
Severity: MEDIUM
Source: Microsoft 365 Defender
User reported an email with the subject:
Urgent Payroll Verification Required.

The email contains a link to
secure-northgate-login.example and asks the user to enter
Microsoft 365 credentials. The sender domain was registered
two days ago.
"""


BRUTE_FORCE_ALERT = """
Alert ID: NG-2027-1208
Severity: HIGH
Source: Microsoft 365 Defender

There were 1,847 failed login attempts against 32 employee
accounts during a 12-minute period. All attempts originated
from IP 203.0.113.88. Three accounts were successfully
accessed after repeated password attempts.
"""


# ---------------------------------------------------------
# MAIN DEMONSTRATION
# ---------------------------------------------------------

if __name__ == "__main__":
    print("=" * 70)
    print("LAB 1.2 EXERCISE 2: DECOMPOSITION DEMONSTRATION")
    print("=" * 70)

    # -----------------------------------------------------
    # DEMO 1: FIXED DECOMPOSITION
    # -----------------------------------------------------

    fixed_result = run_fixed_intel_digest(
        overnight_feed=OVERNIGHT_FEED,
        asset_inventory=ASSET_INVENTORY
    )

    print("\n" + "=" * 70)
    print("FIXED PIPELINE COMPLETED")
    print("=" * 70)

    print("\nFixed-result keys:")
    print(list(fixed_result.keys()))

    # -----------------------------------------------------
    # DEMO 2: ADAPTIVE DECOMPOSITION
    # -----------------------------------------------------

    print("\n" + "=" * 70)
    print("ADAPTIVE DECOMPOSITION: LIVE ALERT TRIAGE")
    print("=" * 70)

    adaptive_tests = [
        {
            "name": "Data Exfiltration Test",
            "alert": DATA_EXFILTRATION_ALERT,
            "expected_branch": "data_exfiltration"
        },
        {
            "name": "Phishing Test",
            "alert": PHISHING_ALERT,
            "expected_branch": "phishing"
        },
        {
            "name": "Brute-Force Test",
            "alert": BRUTE_FORCE_ALERT,
            "expected_branch": "brute_force"
        }
    ]

    adaptive_results = []

    for test in adaptive_tests:
        print("\n" + "-" * 70)
        print(test["name"])
        print("-" * 70)

        result = run_adaptive_triage(test["alert"])
        adaptive_results.append(result)

        print(f"\nExpected branch: {test['expected_branch']}")
        print(f"Actual branch:   {result['branch']}")

        if result["branch"] == test["expected_branch"]:
            print("Branch test:     PASSED")
        else:
            print("Branch test:     FAILED")

        print("\nSPECIALIST TRIAGE RESPONSE:")
        print(result["answer"])

    # -----------------------------------------------------
    # FINAL SUMMARY
    # -----------------------------------------------------

    print("\n" + "=" * 70)
    print("DECOMPOSITION DEMONSTRATION COMPLETED")
    print("=" * 70)

    print("\nAdaptive branch summary:")

    for number, result in enumerate(adaptive_results, start=1):
        print(f"{number}. {result['branch']}")