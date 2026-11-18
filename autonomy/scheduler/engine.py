from __future__ import annotations

from dataclasses import dataclass

from ..contracts import Event


@dataclass(frozen=True)
class TickResult:
    due_jobs: int
    published_events: int


class SchedulerEngine:
    """Restart-safe interval scheduler. Missed intervals coalesce into one event."""

    def __init__(self, repository, event_bus):
        self.repository=repository
        self.event_bus=event_bus

    def seed_defaults(self) -> None:
        self.repository.upsert_interval_job(
            "autonomy_heartbeat", "autonomy_heartbeat", 60,
            {"purpose":"refresh_local_context"}, priority=20,
        )
        self.repository.upsert_interval_job(
            "morning_briefing", "morning_started", 86400,
            {"purpose":"daily_local_briefing"}, priority=65,
        )

    def tick(self, now_text: str | None = None) -> TickResult:
        jobs=self.repository.claim_due_jobs(now_text)
        published=0
        for job in jobs:
            dedupe=f"{job['job_id']}:{job['claimed_at']}"
            _,created=self.event_bus.publish(Event(
                event_type=job["event_type"], payload=job["payload"],
                priority=job["priority"], source="scheduler", dedupe_key=dedupe,
            ))
            published+=int(created)
        return TickResult(len(jobs),published)
