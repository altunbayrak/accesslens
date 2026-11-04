"""initial schema
Revision ID: 001_initial
"""
from alembic import op
import sqlalchemy as sa
revision = "001_initial"; down_revision = None; branch_labels = None; depends_on = None
def upgrade():
    op.create_table("projects", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("name", sa.String(120), nullable=False), sa.Column("allowed_domains", sa.JSON(), nullable=False), sa.Column("max_pages", sa.Integer(), nullable=False), sa.Column("schedule_cron", sa.String(100)), sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP")))
    op.create_table("scans", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("project_id", sa.Integer(), sa.ForeignKey("projects.id"), nullable=False), sa.Column("status", sa.Enum("queued", "running", "completed", "failed", name="scanstatus"), nullable=False), sa.Column("source", sa.String(40), nullable=False), sa.Column("started_at", sa.DateTime()), sa.Column("completed_at", sa.DateTime()), sa.Column("summary", sa.JSON(), nullable=False), sa.Column("error", sa.Text()))
    op.create_table("findings", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("scan_id", sa.Integer(), sa.ForeignKey("scans.id"), nullable=False), sa.Column("category", sa.String(32), nullable=False), sa.Column("severity", sa.String(16), nullable=False), sa.Column("title", sa.String(255), nullable=False), sa.Column("detail", sa.Text(), nullable=False), sa.Column("remediation", sa.Text(), nullable=False), sa.Column("url", sa.Text()), sa.Column("selector", sa.Text()), sa.Column("evidence", sa.JSON(), nullable=False))
def downgrade():
    op.drop_table("findings"); op.drop_table("scans"); op.drop_table("projects")
