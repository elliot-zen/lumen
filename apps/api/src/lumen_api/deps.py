from fastapi import Depends
from sqlalchemy.orm import Session

from lumen_api.db import get_db
from lumen_api.store import JobStore


def get_job_store(db: Session = Depends(get_db)) -> JobStore:
    return JobStore(db)
