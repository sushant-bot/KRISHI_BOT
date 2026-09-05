"""
Seed demo data for AgroVisor Edge.
Seeds Green Valley Farm with:
- Zone B1: North Field (Score 72, Moisture 28%, Temp 35°C, Light 45k lux, At Risk / Early Blight AI)
- Zone B2: South Orchard (Moisture 24%, Temp 33.2°C, Light 52k lux, High Risk / Flow Failure)
- Zone B3: East Greenhouse (Score 88, Moisture 48%, Temp 26.5°C, Light 38k lux, Healthy)
"""
import os
import shutil
import sys
from datetime import datetime, timezone, timedelta

# Add backend directory to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app.database import SessionLocal, engine, Base
from app.models import (
    Farm, Zone, SensorReading, CropImage, AIResult,
    DecisionResult, IrrigationEvent, IrrigationStatus,
    IrrigationAction, PumpStatus, WaterFlowReading, Alert
)

def seed():
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()

    try:
        # Find or create Green Valley Farm
        farm = session.query(Farm).filter(Farm.name == "Green Valley Farm").first()
        if not farm:
            farm = Farm(name="Green Valley Farm", location="Nashik Agro Valley, Maharashtra")
            session.add(farm)
            session.flush()
        else:
            farm.location = "Nashik Agro Valley, Maharashtra"

        now = datetime.now(timezone.utc)

        # Zones: B1, B2, B3
        zone_configs = [
            {"code": "B1", "name": "North Field"},
            {"code": "B2", "name": "South Orchard"},
            {"code": "B3", "name": "East Greenhouse"},
        ]

        zones = {}
        for zc in zone_configs:
            z = session.query(Zone).filter(Zone.farm_id == farm.id, Zone.code == zc["code"]).first()
            if not z:
                z = Zone(farm_id=farm.id, code=zc["code"], name=zc["name"])
                session.add(z)
                session.flush()
            else:
                z.name = zc["name"]
            zones[zc["code"]] = z

        b1, b2, b3 = zones["B1"], zones["B2"], zones["B3"]

        # 1. Sensor Readings for B1, B2, B3 with historical points
        for i in range(12):
            t = now - timedelta(minutes=(11 - i) * 15)
            # B1: drops to 28%
            session.add(SensorReading(
                zone_id=b1.id,
                timestamp=t,
                soil_moisture=round(34.0 - i * 0.55, 1),
                soil_temperature=round(31.5 + i * 0.3, 1),
                light_intensity=round(42000 + i * 250, 0)
            ))
            # B2: drops to 24%
            session.add(SensorReading(
                zone_id=b2.id,
                timestamp=t,
                soil_moisture=round(30.0 - i * 0.55, 1),
                soil_temperature=round(30.0 + i * 0.28, 1),
                light_intensity=round(48000 + i * 350, 0)
            ))
            # B3: stable around 48%
            session.add(SensorReading(
                zone_id=b3.id,
                timestamp=t,
                soil_moisture=round(46.0 + (i % 3) * 1.0, 1),
                soil_temperature=round(25.5 + (i % 4) * 0.3, 1),
                light_intensity=round(36000 + (i % 5) * 400, 0)
            ))

        # 2. Crop Images & AI Analysis Results
        # B1
        img_b1 = session.query(CropImage).filter(CropImage.zone_id == b1.id).first()
        if not img_b1:
            img_b1 = CropImage(
                farm_id=farm.id,
                zone_id=b1.id,
                image_path="https://images.unsplash.com/photo-1592417817098-8f3d6910985c?w=1000&q=80",
                timestamp=now - timedelta(minutes=14)
            )
            session.add(img_b1)
            session.flush()

        ai_b1 = session.query(AIResult).filter(AIResult.zone_id == b1.id).first()
        if not ai_b1:
            session.add(AIResult(
                image_id=img_b1.id,
                zone_id=b1.id,
                crop_health="At Risk",
                disease="Early Blight",
                confidence=0.91,
                growth_stage="Vegetative",
                provider="simulated-edge-vision-v2"
            ))

        # B2
        img_b2 = session.query(CropImage).filter(CropImage.zone_id == b2.id).first()
        if not img_b2:
            img_b2 = CropImage(
                farm_id=farm.id,
                zone_id=b2.id,
                image_path="https://images.unsplash.com/photo-1592417817038-d13fd7342625?w=1000&q=80",
                timestamp=now - timedelta(minutes=30)
            )
            session.add(img_b2)
            session.flush()

        ai_b2 = session.query(AIResult).filter(AIResult.zone_id == b2.id).first()
        if not ai_b2:
            session.add(AIResult(
                image_id=img_b2.id,
                zone_id=b2.id,
                crop_health="At Risk",
                disease="Water Stress Chlorosis",
                confidence=0.87,
                growth_stage="Fruit Development",
                provider="simulated-edge-vision-v2"
            ))

        # B3
        img_b3 = session.query(CropImage).filter(CropImage.zone_id == b3.id).first()
        if not img_b3:
            img_b3 = CropImage(
                farm_id=farm.id,
                zone_id=b3.id,
                image_path="https://images.unsplash.com/photo-1530836369250-ef72a3f5cda8?w=1000&q=80",
                timestamp=now - timedelta(minutes=45)
            )
            session.add(img_b3)
            session.flush()

        ai_b3 = session.query(AIResult).filter(AIResult.zone_id == b3.id).first()
        if not ai_b3:
            session.add(AIResult(
                image_id=img_b3.id,
                zone_id=b3.id,
                crop_health="Healthy",
                disease="None Detected",
                confidence=0.96,
                growth_stage="Flowering",
                provider="simulated-edge-vision-v2"
            ))

        # 3. Decision Results
        # B1
        dec_b1 = session.query(DecisionResult).filter(DecisionResult.zone_id == b1.id).first()
        if not dec_b1:
            session.add(DecisionResult(
                zone_id=b1.id,
                irrigation_priority="MEDIUM",
                water_stress="HIGH",
                heat_stress="MODERATE",
                disease_spread_risk="LOW",
                yield_risk="MEDIUM",
                farm_health_score=72,
                advisory="Monitor B1 closely. Current conditions indicate that the zone should be monitored for changes in soil moisture and early blight progression. Recommend targeted low-pressure drip irrigation during cooler afternoon hours.",
                provider="agrovisor-edge-intelligence-v1"
            ))

        # B2
        dec_b2 = session.query(DecisionResult).filter(DecisionResult.zone_id == b2.id).first()
        if not dec_b2:
            session.add(DecisionResult(
                zone_id=b2.id,
                irrigation_priority="HIGH",
                water_stress="HIGH",
                heat_stress="HIGH",
                disease_spread_risk="MEDIUM",
                yield_risk="HIGH",
                farm_health_score=46,
                advisory="Critical attention required in B2. Soil moisture has fallen below 25% threshold with elevated soil temperature. Immediate irrigation required once line fault is cleared.",
                provider="agrovisor-edge-intelligence-v1"
            ))

        # B3
        dec_b3 = session.query(DecisionResult).filter(DecisionResult.zone_id == b3.id).first()
        if not dec_b3:
            session.add(DecisionResult(
                zone_id=b3.id,
                irrigation_priority="LOW",
                water_stress="LOW",
                heat_stress="LOW",
                disease_spread_risk="LOW",
                yield_risk="LOW",
                farm_health_score=88,
                advisory="Zone B3 greenhouse environment is optimal. Soil moisture and VPD within target parameters. Maintain current drip schedule.",
                provider="agrovisor-edge-intelligence-v1"
            ))

        # 4. Irrigation Events
        # B1: Active event with 5.6L delivered / 10L target
        ev_b1 = session.query(IrrigationEvent).filter(
            IrrigationEvent.zone_id == b1.id,
            IrrigationEvent.status == IrrigationStatus.ACTIVE
        ).first()
        if not ev_b1:
            ev_b1 = IrrigationEvent(
                zone_id=b1.id,
                command=IrrigationAction.START,
                started_at=now - timedelta(minutes=4),
                target_water_liters=10.0,
                water_delivered_liters=5.6,
                status=IrrigationStatus.ACTIVE
            )
            session.add(ev_b1)
            session.flush()

            # Add flow reading
            session.add(WaterFlowReading(
                irrigation_event_id=ev_b1.id,
                zone_id=b1.id,
                timestamp=now - timedelta(seconds=30),
                flow_rate=2.4,
                water_delivered_liters=5.6,
                pump_status=PumpStatus.ON
            ))

        # B3: Completed event earlier today (10.0 L)
        ev_b3 = session.query(IrrigationEvent).filter(
            IrrigationEvent.zone_id == b3.id,
            IrrigationEvent.status == IrrigationStatus.COMPLETED
        ).first()
        if not ev_b3:
            ev_b3 = IrrigationEvent(
                zone_id=b3.id,
                command=IrrigationAction.START,
                started_at=now - timedelta(hours=3),
                ended_at=now - timedelta(hours=2, minutes=45),
                target_water_liters=10.0,
                water_delivered_liters=10.0,
                status=IrrigationStatus.COMPLETED
            )
            session.add(ev_b3)

        # 5. Alerts
        # High alert for Zone B2 (flow failure or pressure drop)
        alert_b2 = session.query(Alert).filter(Alert.zone_id == b2.id).first()
        if not alert_b2:
            session.add(Alert(
                farm_id=farm.id,
                zone_id=b2.id,
                type="IRRIGATION_FLOW_FAILURE",
                severity="HIGH",
                message="Zone B2: Pump is on but water flow is zero.",
                is_read=False
            ))

        session.commit()
        print("Demo data seeded successfully for Green Valley Farm (Zones B1, B2, B3)!")

    except Exception as e:
        session.rollback()
        print("Error seeding data:", e)
        raise
    finally:
        session.close()

if __name__ == "__main__":
    seed()
    # Sync backend/agrovisor.db to agrovisor.db in root if exists
    backend_db = os.path.join(os.path.dirname(__file__), "agrovisor.db")
    root_db = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "agrovisor.db"))
    if os.path.exists(backend_db):
        shutil.copyfile(backend_db, root_db)
        print(f"Copied {backend_db} -> {root_db}")
