import json
import anthropic


# Create the Anthropic client.
# It automatically reads ANTHROPIC_API_KEY from Windows.
client = anthropic.Anthropic()

# Model used by the specialist subagents.
SUBAGENT_MODEL = "claude-haiku-4-5-20251001"


def get_text(response):
    """
    Extract text from an Anthropic API response.
    """

    text_parts = []

    for block in response.content:
        if block.type == "text":
            text_parts.append(block.text)

    return "\n".join(text_parts).strip()


def parse_json_safely(text):
    """
    Remove common Markdown code fences before parsing JSON.
    """

    cleaned_text = text.strip()

    if cleaned_text.startswith("```json"):
        cleaned_text = cleaned_text[7:]
    elif cleaned_text.startswith("```"):
        cleaned_text = cleaned_text[3:]

    if cleaned_text.endswith("```"):
        cleaned_text = cleaned_text[:-3]

    cleaned_text = cleaned_text.strip()

    return json.loads(cleaned_text)


def run_classifier(ticket):
    """
    Subagent 1:
    Classifies the support ticket.
    """

    response = client.messages.create(
        model=SUBAGENT_MODEL,
        max_tokens=500,
        system=(
            "You are a customer-support ticket classifier. "
            "Classify the ticket into product_area, severity, and intent. "
            "Respond only with a valid JSON object. "
            "Do not include explanations or Markdown."
        ),
        messages=[
            {
                "role": "user",
                "content": f"""
Classify this support ticket.

Allowed product_area values:
Billing, Platform, Integrations, Security, Onboarding

Allowed severity values:
P1-Critical, P2-High, P3-Medium, P4-Low

Allowed intent values:
Bug, Question, Feature Request, Billing Dispute

Ticket:
{ticket}
"""
            }
        ]
    )

    response_text = get_text(response)

    try:
        return parse_json_safely(response_text)

    except json.JSONDecodeError as error:
        raise ValueError(
            f"Classifier returned invalid JSON: {response_text}"
        ) from error


def run_crm_enricher(customer_email, classification):
    """
    Subagent 2:
    Simulates a CRM lookup and returns customer account information.
    """

    response = client.messages.create(
        model=SUBAGENT_MODEL,
        max_tokens=500,
        system=(
            "You are a CRM enrichment specialist. "
            "Simulate a CRM lookup for the supplied customer email. "
            "Return account_tier, sla_tier, account_manager, "
            "and contract_value. "
            "Respond only with a valid JSON object. "
            "Do not include explanations or Markdown."
        ),
        messages=[
            {
                "role": "user",
                "content": f"""
Simulate a CRM lookup using the following information.

Customer email:
{customer_email}

Ticket classification:
{json.dumps(classification, indent=2)}

Return a JSON object containing:
- account_tier
- sla_tier
- account_manager
- contract_value
"""
            }
        ]
    )

    response_text = get_text(response)

    try:
        return parse_json_safely(response_text)

    except json.JSONDecodeError as error:
        raise ValueError(
            f"CRM Enricher returned invalid JSON: {response_text}"
        ) from error


def run_drafter(ticket, classification, crm):
    """
    Subagent 3:
    Drafts a professional first-response email.
    """

    context = f"""
Customer support ticket:
{ticket}

Classification:
{json.dumps(classification, indent=2)}

CRM information:
{json.dumps(crm, indent=2)}
"""

    response = client.messages.create(
        model=SUBAGENT_MODEL,
        max_tokens=800,
        system=(
            "You are a customer-support response specialist. "
            "Write a professional first-response email. "
            "Acknowledge the customer's issue and urgency. "
            "Reference the correct product area and SLA tier. "
            "Do not invent technical solutions that are not provided."
        ),
        messages=[
            {
                "role": "user",
                "content": context
            }
        ]
    )

    return get_text(response)


def run_validator(draft, classification, crm):
    """
    Subagent 4:
    Checks the draft before it is sent.
    """

    response = client.messages.create(
        model=SUBAGENT_MODEL,
        max_tokens=500,
        system=(
            "You are a customer-support quality validator. "
            "Check whether the draft references the correct product area, "
            "matches the customer's SLA and account tier, "
            "and uses an appropriate professional tone. "
            "Respond with APPROVED if everything is correct. "
            "Otherwise, provide a short list of specific issues."
        ),
        messages=[
            {
                "role": "user",
                "content": f"""
Validate the following response draft.

Expected product area:
{classification.get("product_area")}

Expected severity:
{classification.get("severity")}

Expected intent:
{classification.get("intent")}

Customer account tier:
{crm.get("account_tier")}

Customer SLA tier:
{crm.get("sla_tier")}

Draft:
{draft}
"""
            }
        ]
    )

    return get_text(response)