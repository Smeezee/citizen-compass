from typing import Literal

from pydantic import BaseModel, ConfigDict


class ManufacturerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    code: str | None


class DealerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    location: str | None


class ShipOut(BaseModel):
    id: int
    name: str
    manufacturer: str
    role: str | None
    notes: str | None
    status: Literal["purchasable", "pledge_only"]
    auec_price: int | None
    dealers: list[str]
    pledge_price_usd: float | None
    pledge_url: str | None
    confidence: str
    last_verified_patch: str | None
