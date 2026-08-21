from context import TicketContext

from subagents import (
    run_classifier,
    run_crm_enricher,
    run_drafter,
    run_validator
)


# Test ticket provided in the lab.
ticket = """
From: sarah.chen@globalcorp.com
Subject: Cannot access SSO login - entire team locked out

Our team of 40 has been unable to log in via SSO since
09:00 this morning. We have a client demo in 3 hours.
This is completely blocking us.
"""


# Create the context object with required intake information.
ctx = TicketContext(
    ticket_id="TICKET-001",
    raw_ticket=ticket,
    customer_email="sarah.chen@globalcorp.com"
)


print("=" * 60)
print("CUSTOMER SUPPORT TRIAGE PIPELINE - VERSION 2")
print("=" * 60)


# Step 1: Classify the support ticket.
print("\nStep 1: Running Classifier...")

classification = run_classifier(ctx.raw_ticket)

# Save classification output into the context object.
ctx.product_area = classification["product_area"]
ctx.severity = classification["severity"]
ctx.intent = classification["intent"]

print("\nCLASSIFIER OUTPUT:")
print(classification)

print("\nClassification complete:")
print(ctx.classification_complete())


# Step 2: Enrich the ticket with CRM information.
print("\nStep 2: Running CRM Enricher...")

# Pass only the fields required by the CRM Enricher.
classification_for_crm = {
    "product_area": ctx.product_area,
    "severity": ctx.severity,
    "intent": ctx.intent
}

crm_data = run_crm_enricher(
    ctx.customer_email,
    classification_for_crm
)

# Save CRM output into the context object.
ctx.account_tier = crm_data["account_tier"]
ctx.sla_tier = crm_data["sla_tier"]
ctx.account_manager = crm_data["account_manager"]

print("\nCRM ENRICHER OUTPUT:")
print(crm_data)

print("\nEnrichment complete:")
print(ctx.enrichment_complete())


# Step 3: Draft the customer response.
print("\nStep 3: Running Drafter...")

# Pass only the specific classification and CRM fields needed.
classification_for_drafter = {
    "product_area": ctx.product_area,
    "severity": ctx.severity,
    "intent": ctx.intent
}

crm_for_drafter = {
    "account_tier": ctx.account_tier,
    "sla_tier": ctx.sla_tier,
    "account_manager": ctx.account_manager
}

draft = run_drafter(
    ctx.raw_ticket,
    classification_for_drafter,
    crm_for_drafter
)

# Save the draft into the context object.
ctx.draft_response = draft

print("\nDRAFTER OUTPUT:")
print(ctx.draft_response)

print("\nDraft complete:")
print(ctx.draft_complete())


# Step 4: Validate the customer response.
print("\nStep 4: Running Validator...")

# Pass only the fields required by the Validator.
classification_for_validator = {
    "product_area": ctx.product_area,
    "severity": ctx.severity,
    "intent": ctx.intent
}

crm_for_validator = {
    "account_tier": ctx.account_tier,
    "sla_tier": ctx.sla_tier,
    "account_manager": ctx.account_manager
}

validation = run_validator(
    ctx.draft_response,
    classification_for_validator,
    crm_for_validator
)

# Save the validation result into the context object.
ctx.validation_result = validation

print("\nVALIDATOR OUTPUT:")
print(ctx.validation_result)


# Print the complete context object.
print("\n" + "=" * 60)
print("FINAL TICKET CONTEXT")
print("=" * 60)

print(ctx)

print("\n" + "=" * 60)
print("PIPELINE VERSION 2 COMPLETED")
print("=" * 60)