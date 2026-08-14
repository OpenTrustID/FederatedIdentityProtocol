import logging
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .config import settings
from .models import Endorsement, Identity, TrustGraph
from .trust import compute_trust_scores

logger = logging.getLogger("opentrust")

app = FastAPI(title="OpenTrust ID", description="Federated identity via trust graph endorsements")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory graph (single instance for simplicity)
graph = TrustGraph()


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "identities": len(graph.identities),
        "endorsements": len(graph.endorsements),
    }


# --- Request schemas ---

class IdentityCreate(BaseModel):
    name: str
    metadata: dict = {}


class EndorsementCreate(BaseModel):
    endorser_id: str
    endorsee_id: str
    weight: float = 1.0
    note: Optional[str] = None


# --- Identity endpoints ---

@app.post("/identities", response_model=Identity, status_code=201)
def create_identity(body: IdentityCreate):
    identity = Identity(name=body.name, metadata=body.metadata)
    graph.add_identity(identity)
    logger.info("identity created id=%s name=%r", identity.id, identity.name)
    return identity


@app.get("/identities", response_model=list[Identity])
def list_identities():
    return list(graph.identities.values())


@app.get("/identities/{identity_id}", response_model=Identity)
def get_identity(identity_id: str):
    if identity_id not in graph.identities:
        raise HTTPException(status_code=404, detail="Identity not found")
    return graph.identities[identity_id]


@app.delete("/identities/{identity_id}", status_code=204)
def delete_identity(identity_id: str):
    if identity_id not in graph.identities:
        raise HTTPException(status_code=404, detail="Identity not found")
    del graph.identities[identity_id]
    graph.endorsements[:] = [
        e for e in graph.endorsements
        if e.endorser_id != identity_id and e.endorsee_id != identity_id
    ]
    logger.info("identity deleted id=%s", identity_id)


@app.get("/identities/{identity_id}/endorsers", response_model=list[Endorsement])
def get_endorsers(identity_id: str):
    """Endorsements received by this identity (who vouches for them)."""
    if identity_id not in graph.identities:
        raise HTTPException(status_code=404, detail="Identity not found")
    return graph.get_endorsements_for(identity_id)


@app.get("/identities/{identity_id}/endorsees", response_model=list[Endorsement])
def get_endorsees(identity_id: str):
    """Endorsements given by this identity (who they vouch for)."""
    if identity_id not in graph.identities:
        raise HTTPException(status_code=404, detail="Identity not found")
    return graph.get_endorsements_by(identity_id)


# --- Endorsement endpoints ---

@app.post("/endorsements", response_model=Endorsement, status_code=201)
def create_endorsement(body: EndorsementCreate):
    try:
        endorsement = Endorsement(**body.model_dump())
        endorsement = graph.add_endorsement(endorsement)
        logger.info(
            "endorsement recorded endorser=%s endorsee=%s weight=%.2f",
            endorsement.endorser_id, endorsement.endorsee_id, endorsement.weight,
        )
        return endorsement
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/endorsements", response_model=list[Endorsement])
def list_endorsements():
    return graph.endorsements


@app.delete("/endorsements/{endorsement_id}", status_code=204)
def delete_endorsement(endorsement_id: str):
    if not graph.remove_endorsement(endorsement_id):
        raise HTTPException(status_code=404, detail="Endorsement not found")


# --- Trust score endpoints ---

@app.get("/trust-scores")
def get_trust_scores() -> dict[str, float]:
    return compute_trust_scores(graph)


@app.get("/trust-scores/{identity_id}")
def get_trust_score(identity_id: str) -> dict:
    if identity_id not in graph.identities:
        raise HTTPException(status_code=404, detail="Identity not found")
    scores = compute_trust_scores(graph)
    return {"identity_id": identity_id, "score": scores.get(identity_id, 0.0)}
