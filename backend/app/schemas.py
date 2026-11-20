from datetime import datetime, timezone
from typing import Literal
from pydantic import BaseModel, Field, ConfigDict

ProductType = Literal["L", "M", "H"]

class MachineCreate(BaseModel):
    code: str = Field(min_length=1, max_length=32)
    name: str = Field(min_length=1, max_length=120)
    asset_type: str = Field(default="rotating_machine", max_length=80)

class MachineRead(MachineCreate):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class MeasurementCreate(BaseModel):
    machine_code: str = Field(min_length=1, max_length=32)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    product_type: ProductType
    air_temperature_k: float = Field(ge=250, le=400)
    process_temperature_k: float = Field(ge=250, le=450)
    rotational_speed_rpm: float = Field(gt=0, le=10000)
    torque_nm: float = Field(ge=0, le=500)
    tool_wear_min: float = Field(ge=0, le=1000)

class MeasurementRead(MeasurementCreate):
    id: int
    machine_id: int
    model_config = ConfigDict(from_attributes=True)

class HealthResponse(BaseModel):
    status: str
    service: str
    database: str

class IngestResponse(BaseModel):
    measurement: MeasurementRead
    inference_status: str
    message: str
