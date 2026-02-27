from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from app.database import get_session

SessionDependence = Annotated[AsyncSession, Depends(get_session)]
