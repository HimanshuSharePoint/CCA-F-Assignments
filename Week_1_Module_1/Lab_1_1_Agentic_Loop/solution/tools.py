import random

def classify_ticket(ticket_text, fields_needed):
    values = {
        "product_area": random.choice(
            ["Billing", "Platform", "Integrations", "Security", "Onboarding"]
        ),
        "severity": random.choice(
            ["P1-Critical", "P2-High", "P3-Medium", "P4-Low"]
        ),
        "intent": random.choice(
            ["Bug", "Question", "Feature Request", "Billing Dispute"]
        )
    }

    return {field: values[field] for field in fields_needed}