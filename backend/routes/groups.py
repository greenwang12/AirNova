from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from backend.db import get_session
from backend.model import GroupBooking
from backend.routes.auth_dependency import get_current_user, security

router = APIRouter(prefix="/groups", tags=["Groups"])


# =========================
# CREATE GROUP
# =========================
@router.post("/create", dependencies=[Depends(security)])
def create_group(
    name: str,
    user: dict = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    g = GroupBooking(
        Name=name,
        Owner_Customer_ID=user["user_id"],
        Members=[user["user_id"]],
    )
    session.add(g)
    session.commit()
    session.refresh(g)
    return g


# =========================
# INVITE MEMBER
# =========================
@router.post("/{group_id}/invite", dependencies=[Depends(security)])
def invite_member(
    group_id: int,
    member_id: int,
    user: dict = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    g = session.get(GroupBooking, group_id)
    if not g:
        raise HTTPException(404, "Group not found")

    # ❌ only owner can invite
    if g.Owner_Customer_ID != user["user_id"]:
        raise HTTPException(403, "Only owner can invite members")

    members = g.Members or []
    if member_id not in members:
        members.append(member_id)

    g.Members = members
    session.add(g)
    session.commit()
    session.refresh(g)
    return g


# =========================
# GET GROUP
# =========================
@router.get("/{group_id}", dependencies=[Depends(security)])
def get_group(
    group_id: int,
    user: dict = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    g = session.get(GroupBooking, group_id)
    if not g:
        raise HTTPException(404, "Group not found")

    # ❌ only members can view
    if user["user_id"] not in (g.Members or []):
        raise HTTPException(403, "Not a group member")

    return g
