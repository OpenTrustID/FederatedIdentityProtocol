from __future__ import annotations
from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field
import uuid


class Identity(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict = Field(default_factory=dict)


class Endorsement(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    endorser_id: str
    endorsee_id: str
    weight: float = Field(default=1.0, ge=0.0, le=1.0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    note: Optional[str] = None


class TrustGraph(BaseModel):
    identities: dict[str, Identity] = Field(default_factory=dict)
    endorsements: list[Endorsement] = Field(default_factory=list)

    def add_identity(self, identity: Identity) -> Identity:
        self.identities[identity.id] = identity
        return identity

    def add_endorsement(self, endorsement: Endorsement) -> Endorsement:
        if endorsement.endorser_id not in self.identities:
            raise ValueError(f"Endorser {endorsement.endorser_id} not found")
        if endorsement.endorsee_id not in self.identities:
            raise ValueError(f"Endorsee {endorsement.endorsee_id} not found")
        if endorsement.endorser_id == endorsement.endorsee_id:
            raise ValueError("Cannot endorse yourself")
        self.endorsements.append(endorsement)
        return endorsement

    def get_endorsements_for(self, identity_id: str) -> list[Endorsement]:
        return [e for e in self.endorsements if e.endorsee_id == identity_id]

    def get_endorsements_by(self, identity_id: str) -> list[Endorsement]:
        return [e for e in self.endorsements if e.endorser_id == identity_id]
