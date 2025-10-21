from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from ..deps import SessionDep
from model import String, StringPayload
from ..lib.helpers import is_palindrome, unique_characters, word_count, format_response, hash_string, build_response
from datetime import datetime, timezone


from sqlmodel import select, and_

router = APIRouter(
    prefix='/strings',
    tags=['strings']
)

@router.post('/')
async def create_string(session: SessionDep, string: StringPayload):
    if not string.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='invalid request body or missing value field'
        )
    str_hash = hash_string(string.value)
    str_in_db = session.exec(select(String).where(String.id == str_hash)).first()
    if str_in_db:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='String already exists in the system'
        )
    del str_in_db

    str_is_palindrome = is_palindrome(string.value)
    str_unique_chr = unique_characters(string.value)
    str_word_count = word_count(string.value)

    string_db_obj = String(
        id=str_hash,
        value=string.value,
        length=len(string.value),
        is_palindrome=str_is_palindrome,
        unique_characters=str_unique_chr,
        word_count=str_word_count,
        sha256_hash=str_hash,
        created_at=datetime.now(timezone.utc)
    )

    session.add(string_db_obj)
    session.commit()

    response = format_response(string_db_obj)

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=response
    )


@router.get('/')
async def get_string_filtered(
    session: SessionDep, 
    is_palindrome: bool | None = None, 
    min_length: int | None = None, 
    max_length: int | None = None, 
    word_count: int | None = None, 
    contains_character: str | None = None
):
    if any(param is None for param in [is_palindrome, min_length, max_length, word_count, contains_character]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Invalid query parameter value'
        )

    db_result = session.exec(select(String).where(and_(
        String.is_palindrome == is_palindrome, 
        String.length >= min_length, # type: ignore
        String.length <= max_length, # type: ignore
        String.word_count == word_count,
        String.value.ilike(f"%{contains_character}%") # type: ignore
    ))).all()

    data = [format_response(s) for s in db_result]

    return {
        "data": data,
        "count": len(data),
        "filters_applied": {
            "is_palindrome": is_palindrome,
            "min_length": min_length,
            "max_length": max_length,
            "word_count": word_count,
            "contains_character": contains_character
        }
    }


@router.get('/filter-by-natural-language')
async def filter_by_natural_language(session: SessionDep, query: str | None = None):
    supported_operations = {
        'all single word palindromic strings': 0,
        'strings longer than 10 characters': 1,
        'palindromic strings that contain the first vowel': 2,
        'strings containing the letter z': 3,
    }
    if not query:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Unable to parse natural language query'
        )
    if not query in supported_operations:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Unable to parse natural language query'
        )
    
    match supported_operations[query]:
        case 0:
            db_result = session.exec(select(String).where(and_(String.is_palindrome == True, String.word_count == 1))).all()
            return build_response(db_result, 'all single word palindrome strings', {
                    'word_count': 1,
                    'is_palindrome': True
                })
        
        case 1:
            db_result = session.exec(select(String).where(String.length > 10)).all()
            return build_response(db_result, 'strings longer than 10 characters', {
                    'min_length': 11
                })
        
        case 2:
            db_result = session.exec(select(String).where(and_(
                String.is_palindrome == True,
                String.value.ilike('%a%') # type: ignore
            ))).all()
            return build_response(db_result, 'palindromic strings that contain the first vowel', {
                    'is_palindrome': True,
                    'contains_character': 'a'
                })
        
        case _:
            db_result = session.exec(select(String).where(String.value.contains('z'))).all() # type: ignore
            return build_response(db_result, 'strings containing the letter z', {
                    'contains_character': 'z'
                })



@router.get('/{string_value}/')
async def get_specific_string(session: SessionDep, string_value: str):
    string_id = hash_string(string_value)
    string = session.exec(select(String).where(String.id == string_id)).first()
    if not string:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='String does not exist in the system'
        )
    response = format_response(string)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=response
    )


@router.delete('/{string_value_d}/')
async def delete_string(session: SessionDep, string_value_d: str):
    str_in_db = session.exec(select(String).where(String.id == hash_string(string_value_d))).first()
    if not str_in_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='String does not exist in the system'
        )
    session.delete(str_in_db)
    session.commit()

    return JSONResponse(
        status_code=status.HTTP_204_NO_CONTENT,
        content={}
    )