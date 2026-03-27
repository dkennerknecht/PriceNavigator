from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.entities import OptimizationRun, OptimizationRunItem


def list_runs(session: Session, shopping_list_id: int | None = None) -> list[OptimizationRun]:
    statement = (
        select(OptimizationRun)
        .options(selectinload(OptimizationRun.items))
        .order_by(OptimizationRun.created_at.desc())
    )
    if shopping_list_id is not None:
        statement = statement.where(OptimizationRun.shopping_list_id == shopping_list_id)
    return list(session.scalars(statement).all())


def get_run(session: Session, run_id: int) -> OptimizationRun | None:
    statement = (
        select(OptimizationRun)
        .where(OptimizationRun.id == run_id)
        .options(selectinload(OptimizationRun.items))
    )
    return session.scalar(statement)


def create_run(session: Session, payload: dict, items: list[dict]) -> OptimizationRun:
    run = OptimizationRun(**payload)
    session.add(run)
    session.flush()
    for item_payload in items:
        session.add(OptimizationRunItem(optimization_run_id=run.id, **item_payload))
    session.commit()
    statement = (
        select(OptimizationRun)
        .where(OptimizationRun.id == run.id)
        .options(selectinload(OptimizationRun.items))
    )
    return session.scalar(statement)


def delete_run(session: Session, run: OptimizationRun) -> None:
    session.delete(run)
    session.commit()
