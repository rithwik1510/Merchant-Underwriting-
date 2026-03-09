from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import CategoryBenchmark
from app.schemas import CategoryBenchmarkResponse


router = APIRouter()


@router.get("", response_model=list[CategoryBenchmarkResponse])
def list_benchmarks(db: Session = Depends(get_db)) -> list[CategoryBenchmarkResponse]:
    benchmarks = db.scalars(select(CategoryBenchmark).order_by(CategoryBenchmark.category)).all()
    return [CategoryBenchmarkResponse.model_validate(benchmark) for benchmark in benchmarks]


@router.get("/{category}", response_model=CategoryBenchmarkResponse)
def get_benchmark(category: str, db: Session = Depends(get_db)) -> CategoryBenchmarkResponse:
    benchmark = db.scalar(select(CategoryBenchmark).where(CategoryBenchmark.category == category))
    if not benchmark:
        raise HTTPException(status_code=404, detail="Benchmark not found")
    return CategoryBenchmarkResponse.model_validate(benchmark)
