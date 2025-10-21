from sqlmodel import SQLModel, Field
from datetime import datetime

class String(SQLModel, table=True):
    id: str = Field(unique=True, primary_key=True)
    value: str
    length: int
    is_palindrome: bool
    unique_characters: int
    word_count: int 
    sha256_hash: str
    created_at: datetime

class StringPayload(SQLModel):
    value: str | None = None