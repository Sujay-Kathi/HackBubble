"""001_initial_schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-11-16 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import pgvector
import pgvector.sqlalchemy

# revision identifiers, used by Alembic.
revision: str = '001_initial_schema'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 0. Ensure vector extension is enabled
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    # 1. Users & Profiles
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('auth_subject', sa.String(255), nullable=False, unique=True),
        sa.Column('hashed_password', sa.String(255), nullable=True),
        sa.Column('account_status', sa.String(32), nullable=False, server_default='active'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_users_id', 'users', ['id'])
    op.create_index('ix_users_email', 'users', ['email'])
    op.create_index('ix_users_auth_subject', 'users', ['auth_subject'])

    op.create_table(
        'user_profiles',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('display_name', sa.String(100), nullable=False),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('education_summary', sa.Text(), nullable=True),
        sa.Column('location', sa.String(100), nullable=True),
        sa.Column('domains_of_interest', postgresql.JSONB(), server_default='[]', nullable=False),
        sa.Column('roles_of_interest', postgresql.JSONB(), server_default='[]', nullable=False),
        sa.Column('profile_visibility', sa.String(32), server_default='public', nullable=False),
        sa.Column('resume_sharing', sa.String(32), server_default='leaders_only', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_user_profiles_user_id', 'user_profiles', ['user_id'])

    op.create_table(
        'user_skills',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('skill_name', sa.String(100), nullable=False),
        sa.Column('normalized_skill', sa.String(100), nullable=False),
        sa.Column('proficiency', sa.String(32), server_default='intermediate', nullable=False),
        sa.Column('evidence_source', sa.String(32), server_default='self_reported', nullable=False),
        sa.Column('evidence_text', sa.Text(), nullable=True),
        sa.Column('verified_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_user_skills_user_id', 'user_skills', ['user_id'])
    op.create_index('ix_user_skills_normalized_skill', 'user_skills', ['normalized_skill'])

    op.create_table(
        'user_projects',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('technologies', postgresql.JSONB(), server_default='[]', nullable=False),
        sa.Column('contribution', sa.Text(), nullable=True),
        sa.Column('outcome', sa.Text(), nullable=True),
        sa.Column('project_url', sa.String(500), nullable=True),
        sa.Column('visibility', sa.String(32), server_default='public', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_user_projects_user_id', 'user_projects', ['user_id'])

    op.create_table(
        'user_experience',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('organization', sa.String(200), nullable=False),
        sa.Column('role', sa.String(150), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('is_current', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('evidence_source', sa.String(32), server_default='self_reported', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_user_experience_user_id', 'user_experience', ['user_id'])

    op.create_table(
        'user_achievements',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('issuer', sa.String(150), nullable=True),
        sa.Column('date', sa.Date(), nullable=True),
        sa.Column('evidence_url', sa.String(500), nullable=True),
        sa.Column('verification_status', sa.String(32), server_default='unverified', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_user_achievements_user_id', 'user_achievements', ['user_id'])

    # 2. Hackathons & Sources
    op.create_table(
        'hackathon_sources',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False, unique=True),
        sa.Column('base_url', sa.String(500), nullable=False),
        sa.Column('adapter_key', sa.String(100), nullable=False, unique=True),
        sa.Column('enabled', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('crawl_interval_hours', sa.Integer(), server_default='6', nullable=False),
        sa.Column('policy_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        'scrape_runs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('source_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('hackathon_sources.id', ondelete='CASCADE'), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('finished_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', sa.String(32), server_default='running', nullable=False),
        sa.Column('events_found', sa.Integer(), server_default='0', nullable=False),
        sa.Column('events_created', sa.Integer(), server_default='0', nullable=False),
        sa.Column('events_updated', sa.Integer(), server_default='0', nullable=False),
        sa.Column('error_summary', sa.Text(), nullable=True),
    )
    op.create_index('ix_scrape_runs_source_id', 'scrape_runs', ['source_id'])

    op.create_table(
        'hackathons',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('title', sa.String(300), nullable=False),
        sa.Column('organizer', sa.String(200), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('themes', postgresql.JSONB(), server_default='[]', nullable=False),
        sa.Column('eligibility', sa.Text(), nullable=True),
        sa.Column('mode', sa.String(32), server_default='online', nullable=False),
        sa.Column('location', sa.String(200), nullable=True),
        sa.Column('registration_url', sa.String(1000), nullable=True),
        sa.Column('event_url', sa.String(1000), nullable=False),
        sa.Column('source_name', sa.String(100), nullable=False),
        sa.Column('source_url', sa.String(1000), nullable=False),
        sa.Column('source_event_id', sa.String(200), nullable=True),
        sa.Column('registration_deadline', sa.DateTime(timezone=True), nullable=True),
        sa.Column('start_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('end_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('prize_pool_amount', sa.Numeric(12, 2), nullable=True),
        sa.Column('prize_pool_currency', sa.String(10), nullable=True),
        sa.Column('status', sa.String(32), server_default='upcoming', nullable=False),
        sa.Column('last_scraped_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_verified_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('data_quality_status', sa.String(32), server_default='verified', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_hackathons_title', 'hackathons', ['title'])
    op.create_index('ix_hackathons_organizer', 'hackathons', ['organizer'])
    op.create_index('ix_hackathons_event_url', 'hackathons', ['event_url'])
    op.create_index('ix_hackathons_source_name', 'hackathons', ['source_name'])
    op.create_index('ix_hackathons_status', 'hackathons', ['status'])

    op.create_table(
        'hackathon_source_records',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('hackathon_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('hackathons.id', ondelete='CASCADE'), nullable=False),
        sa.Column('source_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('hackathon_sources.id', ondelete='CASCADE'), nullable=False),
        sa.Column('source_event_id', sa.String(200), nullable=True),
        sa.Column('source_url', sa.String(1000), nullable=False),
        sa.Column('raw_payload', postgresql.JSONB(), server_default='{}', nullable=False),
        sa.Column('last_scraped_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_hackathon_source_records_hackathon_id', 'hackathon_source_records', ['hackathon_id'])
    op.create_index('ix_hackathon_source_records_source_id', 'hackathon_source_records', ['source_id'])

    op.create_table(
        'saved_hackathons',
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('hackathon_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('hackathons.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # 3. Teams & Workflow
    op.create_table(
        'teams',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('hackathon_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('hackathons.id', ondelete='CASCADE'), nullable=False),
        sa.Column('leader_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('name', sa.String(150), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('problem_statement', sa.Text(), nullable=False),
        sa.Column('project_idea', sa.Text(), nullable=True),
        sa.Column('target_size', sa.Integer(), server_default='4', nullable=False),
        sa.Column('current_size', sa.Integer(), server_default='1', nullable=False),
        sa.Column('visibility', sa.String(32), server_default='public', nullable=False),
        sa.Column('status', sa.String(32), server_default='draft', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_teams_hackathon_id', 'teams', ['hackathon_id'])
    op.create_index('ix_teams_leader_id', 'teams', ['leader_id'])
    op.create_index('ix_teams_status', 'teams', ['status'])

    op.create_table(
        'team_roles',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('team_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('teams.id', ondelete='CASCADE'), nullable=False),
        sa.Column('role_name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('vacancy_count', sa.Integer(), server_default='1', nullable=False),
        sa.Column('priority', sa.Integer(), server_default='1', nullable=False),
        sa.Column('mandatory_skills', postgresql.JSONB(), server_default='[]', nullable=False),
        sa.Column('preferred_skills', postgresql.JSONB(), server_default='[]', nullable=False),
        sa.Column('experience_level', sa.String(32), server_default='intermediate', nullable=False),
        sa.Column('role_embedding', pgvector.sqlalchemy.Vector(384), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_team_roles_team_id', 'team_roles', ['team_id'])

    op.create_table(
        'team_preferences',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('team_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('teams.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('time_commitment', sa.String(50), server_default='flexible', nullable=False),
        sa.Column('collaboration_style', sa.String(50), server_default='asynchronous', nullable=False),
        sa.Column('meeting_frequency', sa.String(50), server_default='daily', nullable=False),
        sa.Column('communication_preference', sa.String(50), server_default='discord', nullable=False),
        sa.Column('beginner_friendly', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_team_preferences_team_id', 'team_preferences', ['team_id'])

    op.create_table(
        'team_intelligence',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('team_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('teams.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('problem_embedding', pgvector.sqlalchemy.Vector(384), nullable=True),
        sa.Column('model_name', sa.String(100), server_default='sentence-transformers/all-MiniLM-L6-v2', nullable=False),
        sa.Column('model_version', sa.String(32), server_default='1.0', nullable=False),
        sa.Column('processed_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        'team_applications',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('team_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('teams.id', ondelete='CASCADE'), nullable=False),
        sa.Column('applicant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('role_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('team_roles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('status', sa.String(32), server_default='submitted', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_app_team_applicant_status', 'team_applications', ['team_id', 'applicant_id', 'status'])

    op.create_table(
        'team_invitations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('team_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('teams.id', ondelete='CASCADE'), nullable=False),
        sa.Column('candidate_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('role_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('team_roles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('invited_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('status', sa.String(32), server_default='pending', nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('responded_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_team_invitations_team_id', 'team_invitations', ['team_id'])
    op.create_index('ix_team_invitations_candidate_id', 'team_invitations', ['candidate_id'])

    op.create_table(
        'team_members',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('team_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('teams.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('role_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('team_roles.id', ondelete='SET NULL'), nullable=True),
        sa.Column('membership_status', sa.String(32), server_default='active', nullable=False),
        sa.Column('joined_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('left_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint('team_id', 'user_id', name='uq_team_user_active_member')
    )
    op.create_index('ix_team_members_team_id', 'team_members', ['team_id'])
    op.create_index('ix_team_members_user_id', 'team_members', ['user_id'])

    op.create_table(
        'screening_actions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('team_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('teams.id', ondelete='CASCADE'), nullable=False),
        sa.Column('role_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('team_roles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('leader_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('candidate_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('action', sa.String(32), nullable=False),
        sa.Column('pass_id', sa.Integer(), server_default='1', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_screening_action_team_cand', 'screening_actions', ['team_id', 'candidate_id', 'pass_id'])

    # 4. Resume & Intelligence
    op.create_table(
        'user_resumes',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('storage_key', sa.String(500), nullable=False),
        sa.Column('file_name', sa.String(255), nullable=False),
        sa.Column('file_hash', sa.String(64), nullable=False),
        sa.Column('mime_type', sa.String(100), server_default='application/pdf', nullable=False),
        sa.Column('file_size_bytes', sa.Integer(), nullable=False),
        sa.Column('processing_status', sa.String(32), server_default='uploaded', nullable=False),
        sa.Column('parser_version', sa.String(32), server_default='1.0', nullable=False),
        sa.Column('ocr_used', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('raw_text', sa.Text(), nullable=True),
        sa.Column('parsed_draft', postgresql.JSONB(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_user_resumes_user_id', 'user_resumes', ['user_id'])
    op.create_index('ix_user_resumes_file_hash', 'user_resumes', ['file_hash'])

    op.create_table(
        'candidate_intelligence',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('profile_summary', sa.Text(), nullable=False),
        sa.Column('summary_version', sa.String(32), server_default='1.0', nullable=False),
        sa.Column('model_name', sa.String(100), server_default='gpt-4o-mini', nullable=False),
        sa.Column('source_revision', sa.Integer(), server_default='1', nullable=False),
        sa.Column('generated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        'candidate_embeddings',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('embedding_type', sa.String(32), nullable=False),
        sa.Column('vector', pgvector.sqlalchemy.Vector(384), nullable=False),
        sa.Column('model_name', sa.String(100), server_default='sentence-transformers/all-MiniLM-L6-v2', nullable=False),
        sa.Column('model_version', sa.String(32), server_default='1.0', nullable=False),
        sa.Column('source_revision', sa.Integer(), server_default='1', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_cand_embed_user_type_ver', 'candidate_embeddings', ['user_id', 'embedding_type', 'model_version'])

    # 5. Notifications & Audit
    op.create_table(
        'notifications',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('type', sa.String(50), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('entity_type', sa.String(50), nullable=False),
        sa.Column('entity_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('read_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_notifications_user_id', 'notifications', ['user_id'])
    op.create_index('ix_notifications_created_at', 'notifications', ['created_at'])

    op.create_table(
        'notification_deliveries',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('notification_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('notifications.id', ondelete='CASCADE'), nullable=False),
        sa.Column('provider', sa.String(32), server_default='fcm', nullable=False),
        sa.Column('status', sa.String(32), server_default='queued', nullable=False),
        sa.Column('attempts', sa.Integer(), server_default='0', nullable=False),
        sa.Column('last_error', sa.Text(), nullable=True),
        sa.Column('delivered_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_notification_deliveries_notification_id', 'notification_deliveries', ['notification_id'])

    op.create_table(
        'audit_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('actor_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('entity_type', sa.String(50), nullable=False),
        sa.Column('entity_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('metadata_json', postgresql.JSONB(), server_default='{}', nullable=False),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_audit_logs_action', 'audit_logs', ['action'])
    op.create_index('ix_audit_logs_created_at', 'audit_logs', ['created_at'])


def downgrade() -> None:
    op.drop_table('audit_logs')
    op.drop_table('notification_deliveries')
    op.drop_table('notifications')
    op.drop_table('candidate_embeddings')
    op.drop_table('candidate_intelligence')
    op.drop_table('user_resumes')
    op.drop_table('screening_actions')
    op.drop_table('team_members')
    op.drop_table('team_invitations')
    op.drop_table('team_applications')
    op.drop_table('team_intelligence')
    op.drop_table('team_preferences')
    op.drop_table('team_roles')
    op.drop_table('teams')
    op.drop_table('saved_hackathons')
    op.drop_table('hackathon_source_records')
    op.drop_table('hackathons')
    op.drop_table('scrape_runs')
    op.drop_table('hackathon_sources')
    op.drop_table('user_achievements')
    op.drop_table('user_experience')
    op.drop_table('user_projects')
    op.drop_table('user_skills')
    op.drop_table('user_profiles')
    op.drop_table('users')
    op.execute("DROP EXTENSION IF EXISTS vector;")
