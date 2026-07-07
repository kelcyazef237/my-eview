from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, require_owner, resolve_org_id
from app.database import get_db
from app.models.category_score import CategoryScore
from app.models.organization import Organization
from app.models.report_share import ReportShare
from app.models.score import Score
from app.models.score_history import ScoreHistory
from app.models.tia_entry import TiaEntry
from app.models.user import User
from app.models.vector_finding import VectorFinding
from app.reports.render import build_report_context, render_html, render_pdf
from app.services.jwt import decode_access_token

router = APIRouter()


def _resolve_user_for_report(
    token: str | None,
    user: User | None,
    db: Session,
) -> User:
    """Resolve the user for a report request.

    Browser links (<a href>, iframes) don't send the Authorization header, so
    we also accept a ``token`` query parameter as a fallback.
    """
    if user:
        return user
    if token:
        payload = decode_access_token(token)
        if payload and payload.get("sub"):
            token_user = db.query(User).filter(User.id == payload["sub"]).first()
            if token_user and token_user.is_active:
                return token_user
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")


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


def _score_context(db: Session, user: User, scan_run_id: str | None = None, org_id: str | None = None) -> dict:
    user_org_id = resolve_org_id(user, db, org_id=org_id)

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

    return _load_report_context(db, score, org)


def _load_report_context(db: Session, score: Score, org: Organization) -> dict:
    """Build the Jinja context for a resolved Score + Organization.

    Shared by the authenticated report endpoints and the public short-link
    endpoint, so neither duplicates the eager-loading logic.
    """
    org_id = str(org.id)
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
        .filter_by(org_id=org_id)
        .order_by(ScoreHistory.computed_at.desc())
        .limit(24)
        .all()
    )

    previous_full = (
        db.query(Score)
        .filter(
            Score.org_id == org_id,
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
def report_html(
    scan_run_id: str,
    token: str | None = Query(None),
    org_id: str | None = Query(None),
    user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Render the HTML report for a specific scan run.

    Accepts a ``token`` query parameter as fallback when the Authorization
    header isn't sent (e.g. browser <a> links, iframes), and an optional
    ``org_id`` so a global admin can view any org's report (without it, the
    admin's own org is assumed and cross-org reports 404).
    """
    resolved_user = _resolve_user_for_report(token, user, db)
    context = _score_context(db, resolved_user, scan_run_id, org_id=org_id)
    html = render_html(context)
    return Response(content=html, media_type="text/html")


@router.get("/{scan_run_id}/pdf")
def report_pdf(
    scan_run_id: str,
    token: str | None = Query(None),
    org_id: str | None = Query(None),
    user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Render the PDF report for a specific scan run."""
    resolved_user = _resolve_user_for_report(token, user, db)
    context = _score_context(db, resolved_user, scan_run_id, org_id=org_id)
    try:
        pdf_bytes = render_pdf(context)
    except Exception as exc:  # noqa: BLE001 - surface a clear error instead of a hang
        import logging
        logging.getLogger("myeview.reports").exception("PDF render failed for scan_run %s", scan_run_id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Report PDF could not be generated")
    filename = f"myeview-report-{context['org']['domain']}-{scan_run_id}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


def _generate_share_code(db: Session) -> str:
    """Generate a unique short capability code for a report share."""
    import secrets
    import string
    alphabet = string.ascii_letters + string.digits
    for _ in range(8):
        code = "".join(secrets.choice(alphabet) for _ in range(10))
        if not db.query(ReportShare).filter_by(code=code).first():
            return code
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not generate unique share code")


@router.post("/{scan_run_id}/share")
def create_report_share(
    scan_run_id: str,
    org_id: str | None = Query(None),
    user: User = Depends(require_owner),
    db: Session = Depends(get_db),
):
    """Mint a short, shareable capability link for a report.

    The link embeds no JWT and requires no auth to view — possession of the
    code is the authorization. Reuses an existing active share for the same
    scan run by the same user if one exists, so the link stays stable.
    ``org_id`` lets a global admin mint a share for any org's report.
    """
    # Verify the caller may access this scan run (reuses auth path).
    _score_context(db, user, scan_run_id, org_id=org_id)

    score = db.query(Score).filter(Score.scan_run_id == scan_run_id).first()
    if not score:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found for this scan run")

    existing = (
        db.query(ReportShare)
        .filter_by(scan_run_id=score.scan_run_id, created_by=user.id, revoked=False)
        .order_by(ReportShare.created_at.desc())
        .first()
    )
    if existing:
        code = existing.code
    else:
        code = _generate_share_code(db)
        db.add(ReportShare(
            code=code,
            scan_run_id=score.scan_run_id,
            org_id=score.org_id,
            created_by=user.id,
        ))
        db.commit()

    return {"code": code, "path": f"/api/r/{code}"}
