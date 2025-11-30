from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from ..db import get_session
from ..model import GroupBooking

router = APIRouter(prefix="/groups", tags=["groups"])

@router.post("/create")
def create_group(name: str, owner_id: int, session: Session = Depends(get_session)):
    g = GroupBooking(Name=name, Owner_Customer_ID=owner_id, Members=[owner_id])
    session.add(g); session.commit(); session.refresh(g)
    return g

@router.post("/{group_id}/invite")
def invite_member(group_id: int, member_id: int, session: Session = Depends(get_session)):
    g = session.get(GroupBooking, group_id)
    if not g:
        raise HTTPException(status_code=404, detail="group not found")
    members = g.Members or []
    if member_id not in members:
        members.append(member_id)
    g.Members = members
    session.add(g); session.commit(); session.refresh(g)
    return g

@router.get("/{group_id}")
def get_group(group_id: int, session: Session = Depends(get_session)):
    g = session.get(GroupBooking, group_id)
    if not g:
        raise HTTPException(status_code=404, detail="group not found")
    return g
