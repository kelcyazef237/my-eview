from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from app.api.dependencies import require_owner, resolve_org_id
from app.database import get_db
from app.models.category_score import CategoryScore
from app.models.organization import Organization
from app.models.score import Score
from app.models.score_history import ScoreHistory
from app.models.tia_entry import TiaEntry
from app.models.user import User
from app.models.vector_finding import VectorFinding
from app.reports.render import build_report_context, render_html, render_pdf

router = APIRouter()


def _latest_score_for_org(db: Session, org_id: str) -> Score:
    score = (
        db.query(Score)
        .filter(Score.org_id == org_id)
        .order_by(Score.computed_at.desc())
        .first()
    )
    if not score:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No published score found for this organization",
        )
    return score


def _score_context(db: Session, user: User, scan_run_id: str | None = None) -> dict:
    user_org_id = resolve_org_id(user, db)

    org = db.query(Organization).filter(Organization.id == user_org_id).first()
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )

    if scan_run_id:
        score = db.query(Score).filter(Score.scan_run_id == scan_run_id).first()
        if not score or str(score.org_id) != user_org_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not found for this scan run",
            )
    else:
        score = _latest_score_for_org(db, user_org_id)

    category_scores = (
        db.query(CategoryScore)
        .filter_by(scan_run_id=score.scan_run_id)
        .all()
    )
    tia_entries = (
        db.query(TiaEntry)
        .filter_by(scan_run_id=score.scan_run_id)
        .all()
    )
    vectors = (
        db.query(VectorFinding)
        .filter_by(scan_run_id=score.scan_run_id)
        .all()
    )
    history = (
        db.query(ScoreHistory)
        .filter_by(org_id=user_org_id)
        .order_by(ScoreHistory.computed_at.desc())
        .limit(24)
        .all()
    )

    previous_full = (
        db.query(Score)
        .filter(
            Score.org_id == user_org_id,
            Score.is_full_report == True,
            Score.id != score.id,
        )
        .order_by(Score.computed_at.desc())
        .first()
    )

    return build_report_context(
        org=org,
        score=score,
        category_scores=category_scores,
        tia_entries=tia_entries,
        vectors=vectors,
        history=history,
        previous_full_score=previous_full.overall_score if previous_full else None,
    )


@router.get("/{scan_run_id}")
def report_html(scan_run_id: str, user: User = Depends(require_owner), db: Session = Depends(get_db)):
    """Render the HTML report for a specific scan run."""
    context = _score_context(db, user, scan_run_id)
    html = render_html(context)
    return Response(content=html, media_type="text/html")


@router.get("/{scan_run_id}/pdf")
def report_pdf(scan_run_id: str, user: User = Depends(require_owner), db: Session = Depends(get_db)):
    """Render the PDF report for a specific scan run."""
    context = _score_context(db, user, scan_run_id)
    pdf_bytes = render_pdf(context)
    filename = f"myeview-report-{context['org']['domain']}-{scan_run_id}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
