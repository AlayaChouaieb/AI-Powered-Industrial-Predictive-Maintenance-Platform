from fastapi import FastAPI, Depends, HTTPException\nfrom fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import select, desc
from sqlalchemy.exc import IntegrityError
from .db import Base, engine, get_db
from .models import Machine, Measurement
from .schemas import MachineCreate, MachineRead, MeasurementCreate, MeasurementRead, HealthResponse, IngestResponse

Base.metadata.create_all(bind=engine)

app = FastAPI(title="MotorGuard AI API", version="0.1.0", description="Industrial predictive-maintenance prototype API")\napp.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/health", response_model=HealthResponse)
def health():
    try:
        with engine.connect():
            db_status = "connected"
    except Exception:
        db_status = "unavailable"
    return HealthResponse(status="ok" if db_status == "connected" else "degraded", service="motorguard-api", database=db_status)

@app.post("/api/machines", response_model=MachineRead, status_code=201)
def create_machine(payload: MachineCreate, db: Session = Depends(get_db)):
    machine = Machine(**payload.model_dump())
    db.add(machine)
    try:
        db.commit()
        db.refresh(machine)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Machine code already exists")
    return machine

@app.get("/api/machines", response_model=list[MachineRead])
def list_machines(db: Session = Depends(get_db)):
    return db.scalars(select(Machine).order_by(Machine.id)).all()

@app.post("/api/measurements", response_model=IngestResponse, status_code=201)
def ingest_measurement(payload: MeasurementCreate, db: Session = Depends(get_db)):
    machine = db.scalar(select(Machine).where(Machine.code == payload.machine_code))
    if machine is None:
        raise HTTPException(status_code=404, detail=f"Unknown machine code: {payload.machine_code}. Register it first.")
    values = payload.model_dump(exclude={"machine_code"})
    measurement = Measurement(machine_id=machine.id, **values)
    db.add(measurement)
    db.commit()
    db.refresh(measurement)
    return IngestResponse(
        measurement=MeasurementRead(machine_code=machine.code, **{
            **{k: getattr(measurement, k) for k in values},
            "id": measurement.id,
            "machine_id": measurement.machine_id,
        }),
        inference_status="not_integrated",
        message="Measurement stored. ML inference integration is the next implementation step; no prediction is fabricated."
    )

@app.get("/api/machines/{machine_code}/measurements", response_model=list[MeasurementRead])
def machine_history(machine_code: str, limit: int = 100, db: Session = Depends(get_db)):
    machine = db.scalar(select(Machine).where(Machine.code == machine_code))
    if machine is None:
        raise HTTPException(status_code=404, detail="Machine not found")
    rows = db.scalars(select(Measurement).where(Measurement.machine_id == machine.id).order_by(desc(Measurement.timestamp)).limit(min(max(limit, 1), 500))).all()
    return [MeasurementRead(machine_code=machine.code, **{
        **{k: getattr(row, k) for k in ("timestamp", "product_type", "air_temperature_k", "process_temperature_k", "rotational_speed_rpm", "torque_nm", "tool_wear_min")},
        "id": row.id, "machine_id": row.machine_id
    }) for row in rows]
