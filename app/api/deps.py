from core.db import engine
from typing import Generator, Annotated
from sqlmodel import Session
from fastapi import Depends

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]