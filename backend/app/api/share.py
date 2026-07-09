"""Public short-link report viewer.

A share code is a capability token: anyone holding the code can view the
report, no JWT or user auth required. This is the shareable-link endpoint.
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.organization import Organization
from app.models.report_share import ReportShare
from app.models.score import Score
from app.reports.render import render_html, render_pdf
from app.api.reports import _load_report_context

router = APIRouter()


def _resolve_share(db: Session, code: str) -> ReportShare:
    share = db.query(ReportShare).filter_by(code=code, revoked=False).first()
    if not share:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Link not found or revoked")
    if share.expires_at is not None and share.expires_at <= datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="This share link has expired")
    return share


@router.get("/{code}")
def share_html(code: str, db: Session = Depends(get_db)):
    """Render the HTML report for a short share code (no auth)."""
    share = _resolve_share(db, code)
    score = db.query(Score).filter(Score.scan_run_id == share.scan_run_id).first()
    if not score:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    org = db.query(Organization).filter(Organization.id == share.org_id).first()
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
    context = _load_report_context(db, score, org)
    html = render_html(context)
    return Response(content=html, media_type="text/html")


@router.get("/{code}/pdf")
def share_pdf(code: str, db: Session = Depends(get_db)):
    """Render the PDF report for a short share code (no auth)."""
    share = _resolve_share(db, code)
    score = db.query(Score).filter(Score.scan_run_id == share.scan_run_id).first()
    if not score:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    org = db.query(Organization).filter(Organization.id == share.org_id).first()
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
    context = _load_report_context(db, score, org)
    try:
        pdf_bytes = render_pdf(context)
    except Exception:
        import logging
        logging.getLogger("myeview.reports").exception("PDF render failed for share code %s", share.code)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Report PDF could not be generated")
    filename = f"myeview-report-{context['org']['name'].replace(' ', '-').lower()}-{share.code}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )