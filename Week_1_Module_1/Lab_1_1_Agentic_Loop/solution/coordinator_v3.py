from context import TicketContext

from subagents import (
    run_classifier,
    run_crm_enricher,
    run_drafter,
    run_validator
)

from gates import (
    PipelineGateError,
    gate_classification,
    gate_enrichment,
    gate_draft
)


# Test ticket provided in the lab.
ticket = """
From: sarah.chen@globalcorp.com
Subject: Cannot access SSO login - entire team locked out

Our team of 40 has been unable to log in via SSO since
09:00 this morning. We have a client demo in 3 hours.
This is completely blocking us.
"""


# Create the context with the required starting information.
ctx = TicketContext(
    ticket_id="TICKET-001",
    raw_ticket=ticket,
    customer_email="sarah.chen@globalcorp.com"
)


print("=" * 60)
print("CUSTOMER SUPPORT TRIAGE PIPELINE - VERSION 3")
print("=" * 60)


try:
    # ---------------------------------------------------------
    # STEP 1: CLASSIFIER
    # ---------------------------------------------------------

    print("\nStep 1: Running Classifier...")

    classification = run_classifier(ctx.raw_ticket)

    # Store the classification result in TicketContext.
    ctx.product_area = classification["product_area"]
    ctx.severity = classification["severity"]
    ctx.intent = classification["intent"]

    print("\nCLASSIFIER OUTPUT:")
    print(classification)

    # Gate 1 must pass before CRM Enricher can run.
    gate_classification(ctx)
    print("\nGate 1 passed: Classification is complete.")


    # ---------------------------------------------------------
    # STEP 2: CRM ENRICHER
    # ---------------------------------------------------------

    print("\nStep 2: Running CRM Enricher...")

    classification_for_crm = {
        "product_area": ctx.product_area,
        "severity": ctx.severity,
        "intent": ctx.intent
    }

    crm_data = run_crm_enricher(
        ctx.customer_email,
        classification_for_crm
    )

    # Store CRM results in TicketContext.
    ctx.account_tier = crm_data["account_tier"]
    ctx.sla_tier = crm_data["sla_tier"]
    ctx.account_manager = crm_data["account_manager"]

    print("\nCRM ENRICHER OUTPUT:")
    print(crm_data)

    # Gate 2 must pass before Drafter can run.
    gate_enrichment(ctx)
    print("\nGate 2 passed: CRM enrichment is complete.")


    # ---------------------------------------------------------
    # STEP 3: DRAFTER
    # ---------------------------------------------------------

    print("\nStep 3: Running Drafter...")

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

    # Store the drafted response in TicketContext.
    ctx.draft_response = draft

    print("\nDRAFTER OUTPUT:")
    print(ctx.draft_response)

    # Gate 3 must pass before Validator can run.
    gate_draft(ctx)
    print("\nGate 3 passed: Draft response is available.")


    # ---------------------------------------------------------
    # STEP 4: VALIDATOR
    # ---------------------------------------------------------

    print("\nStep 4: Running Validator...")

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

    # Store the validation result.
    ctx.validation_result = validation

    print("\nVALIDATOR OUTPUT:")
    print(ctx.validation_result)


    # ---------------------------------------------------------
    # PIPELINE COMPLETED
    # ---------------------------------------------------------

    print("\n" + "=" * 60)
    print("FINAL TICKET CONTEXT")
    print("=" * 60)

    print(ctx)

    print("\n" + "=" * 60)
    print("PIPELINE VERSION 3 COMPLETED")
    print("=" * 60)


except PipelineGateError as error:
    print("\n" + "=" * 60)
    print("[PIPELINE BLOCKED]")
    print(error)
    print("=" * 60)