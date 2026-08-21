from dataclasses import dataclass
from typing import Optional


@dataclass
class TicketContext:
    # Required when the ticket enters the pipeline
    ticket_id: str
    raw_ticket: str
    customer_email: str

    # Added by the Classifier
    product_area: Optional[str] = None
    severity: Optional[str] = None
    intent: Optional[str] = None

    # Added by the CRM Enricher
    account_tier: Optional[str] = None
    sla_tier: Optional[str] = None
    account_manager: Optional[str] = None

    # Added by the Drafter and Validator
    draft_response: Optional[str] = None
    validation_result: Optional[str] = None

    def classification_complete(self) -> bool:
        return all([
            self.product_area is not None,
            self.severity is not None,
            self.intent is not None
        ])

    def enrichment_complete(self) -> bool:
        return all([
            self.account_tier is not None,
            self.sla_tier is not None
        ])

    def draft_complete(self) -> bool:
        return self.draft_response is not None