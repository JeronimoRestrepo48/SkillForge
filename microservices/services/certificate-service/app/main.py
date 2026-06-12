from fastapi import FastAPI
import asyncio
import threading
from contextlib import asynccontextmanager
from app.database import engine, Base, SessionLocal
from app.routers import certificates

Base.metadata.create_all(bind=engine)

def consume_events():
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), "../../../../../"))
    from shared.event_bus import RedisEventBus
    import logging
    logger = logging.getLogger("certificate_consumer")
    while True:
        try:
            bus = RedisEventBus()
            for msg_id, event_type, data in bus.consume(stream="ordenes", group_name="certificate_group", consumer_name="certificate_worker"):
                if event_type == "orden.completada":
                    # Process event
                    logger.info(f"Processing orden.completada event: {data}")
                    from app.schemas.certificate import CertificateCheckRequest
                    from app.routers.certificates import check_and_issue_logic
                    req = CertificateCheckRequest(user_id=data.get('user_id'), course_id=data.get('course_id'))
                    db = SessionLocal()
                    try:
                        check_and_issue_logic(req, db)
                    except Exception as e:
                        logger.error(f"Error processing event {msg_id}: {e}")
                    finally:
                        db.close()
        except Exception as e:
            logger.error(f"Event consumer crashed: {e}. Restarting in 5s...")
            import time
            time.sleep(5)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start consumer thread
    thread = threading.Thread(target=consume_events, daemon=True)
    thread.start()
    yield

app = FastAPI(title="SkillForge Certificate Service", lifespan=lifespan)

@app.get("/health")
def health():
    return {"status": "ok", "service": "certificate-service"}

# Registrar router con y sin prefijo para compatibilidad y enrutamiento Nginx
app.include_router(certificates.router, prefix="/api/certificates", tags=["certificates"])
app.include_router(certificates.router, prefix="/certificates", tags=["legacy-certificates"])
app.include_router(certificates.router, tags=["root-certificates"])
