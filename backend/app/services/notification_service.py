"""
Notification service — creates in-app notifications for key HackBubble events.
"""

from __future__ import annotations

import logging
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification
from app.services import delivery_service

logger = logging.getLogger(__name__)

# Notification type constants
NOTIF_APPLICATION_RECEIVED = "application_received"
NOTIF_APPLICATION_SHORTLISTED = "application_shortlisted"
NOTIF_APPLICATION_REJECTED = "application_rejected"
NOTIF_APPLICATION_WITHDRAWN = "application_withdrawn"
NOTIF_INVITATION_RECEIVED = "invitation_received"
NOTIF_INVITATION_ACCEPTED = "invitation_accepted"
NOTIF_INVITATION_DECLINED = "invitation_declined"
NOTIF_TEAM_FINALIZED = "team_finalized"
NOTIF_TEAM_ROLE_FILLED = "team_role_filled"
NOTIF_SCRAPER_RUN_COMPLETE = "scraper_run_complete"


async def create_notification(
    db: AsyncSession,
    *,
    user_id: UUID,
    notif_type: str,
    title: str,
    body: str,
    entity_type: str = "system",
    entity_id: UUID | None = None,
    enqueue_email: bool = True,
) -> Notification:
    """
    Persist a single in-app notification and queue its email delivery.
    Caller must commit.
    """
    notif = Notification(
        user_id=user_id,
        type=notif_type,
        title=title,
        body=body,
        entity_type=entity_type,
        entity_id=entity_id,
    )
    db.add(notif)
    await db.flush()

    if enqueue_email:
        await delivery_service.queue_email_delivery(db, notif)

    logger.info("Created notification type=%s for user=%s", notif_type, user_id)
    return notif


async def notify_application_received(
    db: AsyncSession,
    team_leader_id: UUID,
    applicant_name: str,
    team_name: str,
    team_id: UUID,
    application_id: UUID,
) -> None:
    await create_notification(
        db=db,
        user_id=team_leader_id,
        notif_type=NOTIF_APPLICATION_RECEIVED,
        title="New Application",
        body=f"{applicant_name} applied to join {team_name}.",
        entity_type="team_application",
        entity_id=application_id,
    )


async def notify_application_shortlisted(
    db: AsyncSession,
    applicant_id: UUID,
    team_name: str,
    team_id: UUID,
    application_id: UUID,
) -> None:
    await create_notification(
        db=db,
        user_id=applicant_id,
        notif_type=NOTIF_APPLICATION_SHORTLISTED,
        title="You've been shortlisted!",
        body=f"Your application to {team_name} has been shortlisted.",
        entity_type="team_application",
        entity_id=application_id,
    )


async def notify_application_rejected(
    db: AsyncSession,
    applicant_id: UUID,
    team_name: str,
    team_id: UUID,
    application_id: UUID,
) -> None:
    await create_notification(
        db=db,
        user_id=applicant_id,
        notif_type=NOTIF_APPLICATION_REJECTED,
        title="Application Update",
        body=f"Your application to {team_name} was not accepted this time.",
        entity_type="team_application",
        entity_id=application_id,
    )


async def notify_invitation_received(
    db: AsyncSession,
    candidate_id: UUID,
    team_name: str,
    team_id: UUID,
    invitation_id: UUID,
) -> None:
    await create_notification(
        db=db,
        user_id=candidate_id,
        notif_type=NOTIF_INVITATION_RECEIVED,
        title="Team Invitation",
        body=f"You've been invited to join {team_name}!",
        entity_type="team_invitation",
        entity_id=invitation_id,
    )


async def notify_team_finalized(
    db: AsyncSession,
    member_ids: list[UUID],
    team_name: str,
    team_id: UUID,
) -> None:
    for member_id in member_ids:
        await create_notification(
            db=db,
            user_id=member_id,
            notif_type=NOTIF_TEAM_FINALIZED,
            title="Team Finalized!",
            body=f"Your team {team_name} has been finalized. Good luck at the hackathon!",
            entity_type="team",
            entity_id=team_id,
        )


async def notify_invitation_accepted(
    db: AsyncSession,
    leader_id: UUID,
    candidate_name: str,
    team_name: str,
    invitation_id: UUID,
) -> None:
    await create_notification(
        db=db,
        user_id=leader_id,
        notif_type=NOTIF_INVITATION_ACCEPTED,
        title="Invitation Accepted",
        body=f"{candidate_name} accepted your invitation to join {team_name}.",
        entity_type="team_invitation",
        entity_id=invitation_id,
    )


async def notify_invitation_declined(
    db: AsyncSession,
    leader_id: UUID,
    candidate_name: str,
    team_name: str,
    invitation_id: UUID,
) -> None:
    await create_notification(
        db=db,
        user_id=leader_id,
        notif_type=NOTIF_INVITATION_DECLINED,
        title="Invitation Declined",
        body=f"{candidate_name} declined your invitation to join {team_name}.",
        entity_type="team_invitation",
        entity_id=invitation_id,
    )


async def notify_application_withdrawn(
    db: AsyncSession,
    leader_id: UUID,
    applicant_name: str,
    team_name: str,
    team_id: UUID,
    application_id: UUID,
) -> None:
    await create_notification(
        db=db,
        user_id=leader_id,
        notif_type=NOTIF_APPLICATION_WITHDRAWN,
        title="Application Withdrawn",
        body=f"{applicant_name} withdrew their application to {team_name}.",
        entity_type="team_application",
        entity_id=application_id,
    )
