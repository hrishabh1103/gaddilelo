import os
import asyncio
import traceback
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from sqlalchemy import select, update
from backend.app.core.database import AsyncSessionLocal
from backend.app.models.models import VehicleDiscoveryJob, VehicleDataSource, VehicleDiscoveryRecord, VehicleModel
from backend.app.services.vehicle_intelligence.source_registry import SourceRegistry
from backend.app.services.vehicle_intelligence.discovery_service import DiscoveryService

class VehicleIntelligenceScheduler:
    """
    Background Autonomous Discovery Scheduler.
    Runs periodically independent of user or administrator intervention.
    Enforces concurrency locking, retries transient failures, logs audit trails,
    and records synchronization timestamps.
    """

    _instance: Optional["VehicleIntelligenceScheduler"] = None

    def __init__(self, interval_seconds: Optional[int] = None):
        # Default: 1440 minutes (24 hours) or configured via env var
        env_interval = int(os.getenv("DISCOVERY_SCAN_INTERVAL_MINUTES", "1440")) * 60
        self.interval_seconds = interval_seconds or env_interval
        self.is_running = False
        self._task: Optional[asyncio.Task] = None
        self._lock = asyncio.Lock()
        self.last_sync_timestamp: Optional[datetime] = None
        self.last_sync_status: Optional[str] = None
        self.total_scans_executed: int = 0

    @classmethod
    def get_instance(cls) -> "VehicleIntelligenceScheduler":
        if cls._instance is None:
            cls._instance = VehicleIntelligenceScheduler()
        return cls._instance

    async def start(self, initial_delay_seconds: int = 5):
        """Starts the autonomous scheduler background loop."""
        if os.getenv("ENABLE_BACKGROUND_SCHEDULER", "true").lower() == "false":
            print("[IntelligenceScheduler] Background scheduler disabled via ENABLE_BACKGROUND_SCHEDULER=false.")
            return
        if self.is_running:
            return
        self.is_running = True
        self._task = asyncio.create_task(self._run_loop(initial_delay_seconds))
        print(f"[IntelligenceScheduler] Started background discovery scheduler (Interval: {self.interval_seconds}s)")

    async def stop(self):
        """Gracefully terminates the background scheduler."""
        if not self.is_running:
            return
        self.is_running = False
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        print("[IntelligenceScheduler] Stopped background discovery scheduler")

    async def _run_loop(self, initial_delay: int):
        # Optional warm-up delay after server startup
        if initial_delay > 0:
            await asyncio.sleep(initial_delay)

        while self.is_running:
            try:
                await self.execute_scan_cycle()
            except Exception as e:
                print(f"[IntelligenceScheduler] Unexpected error during scan cycle: {e}")
                traceback.print_exc()

            try:
                await asyncio.sleep(self.interval_seconds)
            except asyncio.CancelledError:
                break

    async def execute_scan_cycle(self) -> Dict[str, Any]:
        """
        Executes a single autonomous discovery scan cycle with concurrency protection,
        retry logic, and persistent database job logging.
        """
        # Duplicate Scan Prevention: Ensure only one scan runs at a time
        if self._lock.locked():
            print("[IntelligenceScheduler] Scan already in progress. Skipping overlapping run.")
            return {"status": "SKIPPED", "reason": "SCAN_ALREADY_IN_PROGRESS"}

        async with self._lock:
            async with AsyncSessionLocal() as db:
                # 1. Create Persistent Job Record
                job = VehicleDiscoveryJob(
                    search_query="AUTONOMOUS_SCHEDULED_SCAN",
                    job_type="SCHEDULED_SCAN",
                    status="IN_PROGRESS"
                )
                db.add(job)
                await db.commit()
                await db.refresh(job)

                adapters = SourceRegistry.list_adapters()
                total_sources = len(adapters)
                scanned_sources = 0
                new_discoveries = 0
                error_messages = []

                for adapter in adapters:
                    # Retry logic with backoff for transient provider errors
                    max_retries = 2
                    success = False
                    announcements = []
                    last_err = None

                    for attempt in range(max_retries):
                        try:
                            announcements = await adapter.fetch_announcements()
                            success = True
                            break
                        except Exception as ex:
                            last_err = str(ex)
                            await asyncio.sleep(1.0 * (attempt + 1))

                    if not success:
                        error_messages.append(f"{adapter.source_name}: {last_err}")
                        adapter.last_error = last_err
                        # Update DB source if exists
                        await db.execute(
                            update(VehicleDataSource)
                            .where(VehicleDataSource.source_name == adapter.source_name)
                            .values(last_error=last_err)
                        )
                        continue

                    # Update adapter success state
                    adapter.last_synced_at = datetime.now(timezone.utc)
                    adapter.last_error = None
                    scanned_sources += 1

                    await db.execute(
                        update(VehicleDataSource)
                        .where(VehicleDataSource.source_name == adapter.source_name)
                        .values(
                            last_synced_at=adapter.last_synced_at,
                            last_error=None
                        )
                    )

                    # Process each discovered vehicle announcement
                    for ann in announcements:
                        model_name = ann.get("model", "")
                        if not model_name:
                            continue

                        # Duplicate Prevention Check: Database check vs Discovery Records & Catalog Models
                        existing_rec = await db.execute(
                            select(VehicleDiscoveryRecord).where(
                                VehicleDiscoveryRecord.discovered_model == model_name
                            )
                        )
                        if existing_rec.scalars().first():
                            continue

                        existing_model = await db.execute(
                            select(VehicleModel).where(
                                VehicleModel.name == model_name
                            )
                        )
                        if existing_model.scalars().first():
                            continue

                        # Ingest new discovered vehicle candidate
                        try:
                            await DiscoveryService.create_customer_discovery_request(
                                search_query=model_name,
                                customer_name="Autonomous Background Scheduler",
                                customer_email="scheduler@gaadilelo.com",
                                customer_phone=None,
                                category_slug=ann.get("category_slug", "car"),
                                target_city_id=None,
                                user_id=None,
                                db=db
                            )
                            new_discoveries += 1
                        except Exception as e:
                            print(f"[IntelligenceScheduler] Failed to ingest '{model_name}': {e}")

                # 2. Finalize Job Status
                if error_messages and new_discoveries == 0 and scanned_sources == 0:
                    job.status = "FAILED"
                    job.error_message = "; ".join(error_messages)
                elif error_messages:
                    job.status = "COMPLETED_WITH_WARNINGS"
                    job.error_message = "; ".join(error_messages)
                else:
                    job.status = "COMPLETED"

                job.completed_at = datetime.now(timezone.utc)
                await db.commit()

                self.last_sync_timestamp = datetime.now(timezone.utc)
                self.last_sync_status = job.status
                self.total_scans_executed += 1

                return {
                    "job_id": job.id,
                    "status": job.status,
                    "sources_scanned": scanned_sources,
                    "total_sources": total_sources,
                    "new_vehicles_discovered": new_discoveries,
                    "errors": error_messages,
                    "completed_at": job.completed_at.isoformat()
                }
