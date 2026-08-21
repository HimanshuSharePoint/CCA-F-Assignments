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

customer_email = "sarah.chen@globalcorp.com"


print("=" * 60)
print("CUSTOMER SUPPORT TRIAGE PIPELINE")
print("=" * 60)


# Step 1: Classify the support ticket.
print("\nStep 1: Running Classifier...")

classification = run_classifier(ticket)

print("\nCLASSIFIER OUTPUT:")
print(classification)


# Step 2: Get customer information from the simulated CRM.
print("\nStep 2: Running CRM Enricher...")

crm_data = run_crm_enricher(
    customer_email,
    classification
)

print("\nCRM ENRICHER OUTPUT:")
print(crm_data)


# Step 3: Create the first-response email.
print("\nStep 3: Running Drafter...")

draft = run_drafter(
    ticket,
    classification,
    crm_data
)

print("\nDRAFTER OUTPUT:")
print(draft)


# Step 4: Validate the drafted response.
print("\nStep 4: Running Validator...")

validation = run_validator(
    draft,
    classification,
    crm_data
)

print("\nVALIDATOR OUTPUT:")
print(validation)


print("\n" + "=" * 60)
print("PIPELINE COMPLETED")
print("=" * 60)