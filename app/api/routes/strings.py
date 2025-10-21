from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from ..deps import SessionDep
from model import String, StringPayload
from ..lib.helpers import is_palindrome, unique_characters, word_count, format_response, hash_string
from datetime import datetime, timezone


from sqlmodel import select

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
    if not all([min_length, max_length, word_count, contains_character]) or is_palindrome == None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Invalid query parameter value'            
        )

    db_result = session.exec(select(String).where(
        String.is_palindrome == is_palindrome, 
        String.length >= min_length, # type: ignore
        String.length <= max_length, # type: ignore
        String.word_count == word_count,
        String.value.contains(contains_character) # type: ignore
    )).all()

    data = [0] * len(db_result)
    count = 0
    for string in db_result:
        data[count] = format_response(string) # type: ignore
        count += 1
    
    response = {}
    response['data'] = data
    response['count'] = count
    response['filters_applied'] = {
        'is_palindrome': is_palindrome,
        'min_length': min_length,
        'max_length': max_length,
        'word_count': word_count,
        'contains_character': contains_character
    }

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=response    
    )


@router.get('/filter-by-natural-language')
async def filter_by_natural_language(session: SessionDep, query: str | None = None):
    supported_operations = {
        'all single word palindrome strings': 0,
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
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail='Query parsed but resulted in conflicting filters'
        )
    
    match supported_operations[query]:
        case 0:
            db_result = session.exec(select(String).where(String.is_palindrome == True, String.word_count == 1)).all()
            data = [0] * len(db_result)
            count = 0
            for string in db_result:
                data[count] = format_response(string) # type: ignore
                count += 1
            response = {}
            response['data'] = data
            response['count'] = count
            response['interpreted_query'] = {
                'original': 'all single word palindrome strings',
                'parsed_filters': {
                    'word_count': 1,
                    'is_palindrome': True
                }
            }
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=response
            )
            
        
        case 1:
            db_result = session.exec(select(String).where(String.length > 10)).all()
            data = [0] * len(db_result)
            count = 0
            for string in db_result:
                data[count] = format_response(string) # type: ignore
                count += 1
            response = {}
            response['data'] = data
            response['count'] = count
            response['interpreted_query'] = {
                'original': 'strings longer than 10 characters',
                'parsed_filters': {
                    'min_length': 11
                }
            }   

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=response
            )
        
        case 2:
            db_result = session.exec(select(String).where(
                String.is_palindrome == True,
                String.value.ilike('%a%') # type: ignore
            )).all()
            data = [0] * len(db_result)
            count = 0
            for string in db_result:
                data[count] = format_response(string) # type: ignore
                count += 1
            response = {}
            response['data'] = data
            response['count'] = count
            response['interpreted_query'] = {
                'original': 'palindromic strings that contain the first vowel',
                'parsed_filters': {
                    'is_palindrome': True,
                    'contains_character': 'a'
                }
            }

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=response    
            )
        
        case _:
            db_result = session.exec(select(String).where(String.value.contains('z'))).all() # type: ignore
            data = [0] * len(db_result)
            count = 0
            for string in db_result:
                data[count] = format_response(string) # type: ignore
                count += 1
            response = {}
            response['data'] = data
            response['count'] = count
            response['interpreted_query'] = {
                'original': 'strings containing the letter z',
                'parsed_filters': {
                    'contains_character': 'z'
                }
            }

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=response
            )


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