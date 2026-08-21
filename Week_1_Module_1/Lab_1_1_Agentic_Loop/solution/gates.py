class PipelineGateError(Exception):
    """
    Custom error raised when a pipeline step is incomplete.
    """

    pass


def gate_classification(ctx):
    """
    Gate 1:
    Checks that classification is complete before CRM enrichment.
    """

    missing_fields = []

    if ctx.product_area is None:
        missing_fields.append("product_area")

    if ctx.severity is None:
        missing_fields.append("severity")

    if ctx.intent is None:
        missing_fields.append("intent")

    if not ctx.classification_complete():
        raise PipelineGateError(
            "Classification is incomplete. "
            f"Missing fields: {', '.join(missing_fields)}. "
            "Rerun the Classifier before continuing."
        )

    return None


def gate_enrichment(ctx):
    """
    Gate 2:
    Checks that CRM enrichment is complete before drafting.
    """

    missing_fields = []

    if ctx.account_tier is None:
        missing_fields.append("account_tier")

    if ctx.sla_tier is None:
        missing_fields.append("sla_tier")

    if not ctx.enrichment_complete():
        raise PipelineGateError(
            "CRM enrichment is incomplete. "
            f"Fields with None values: {', '.join(missing_fields)}. "
            "Rerun the CRM Enricher before continuing."
        )

    return None


def gate_draft(ctx):
    """
    Gate 3:
    Checks that a draft exists before validation.
    """

    if not ctx.draft_complete():
        raise PipelineGateError(
            "Draft is incomplete because draft_response is None. "
            "Rerun the Drafter before continuing."
        )

    return None