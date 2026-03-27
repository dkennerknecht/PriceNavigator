from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_session
from app.repositories import optimization_runs as optimization_repository
from app.schemas.common import DeleteResponse
from app.schemas.optimization import OptimizationRunRead
from app.services.optimization import OptimizationService

router = APIRouter(tags=["optimization"])
optimization_service = OptimizationService()


@router.post("/shopping-lists/{shopping_list_id}/optimize", response_model=OptimizationRunRead)
def optimize_shopping_list(
    shopping_list_id: int,
    session: Session = Depends(get_session),
) -> OptimizationRunRead:
    try:
        result = optimization_service.optimize(session, shopping_list_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return OptimizationRunRead.model_validate(result)


@router.get("/optimization-runs", response_model=list[OptimizationRunRead])
def get_optimization_runs(
    shopping_list_id: int | None = Query(default=None),
    session: Session = Depends(get_session),
) -> list[OptimizationRunRead]:
    return [
        OptimizationRunRead.model_validate(run)
        for run in optimization_repository.list_runs(session, shopping_list_id=shopping_list_id)
    ]


@router.get("/optimization-runs/{run_id}", response_model=OptimizationRunRead)
def get_optimization_run(
    run_id: int, session: Session = Depends(get_session)
) -> OptimizationRunRead:
    run = optimization_repository.get_run(session, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Optimization run not found")
    return OptimizationRunRead.model_validate(run)


@router.delete("/optimization-runs/{run_id}", response_model=DeleteResponse)
def delete_optimization_run(run_id: int, session: Session = Depends(get_session)) -> DeleteResponse:
    run = optimization_repository.get_run(session, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Optimization run not found")
    optimization_repository.delete_run(session, run)
    return DeleteResponse(message="Optimization run deleted")
