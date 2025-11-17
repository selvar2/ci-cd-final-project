from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from ..services.notes_service import Note, notes_service

router = APIRouter(prefix="/api/v1/notes", tags=["notes"])


class NoteCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    content: str = Field(..., min_length=1, max_length=2000)


class NoteResponse(BaseModel):
    id: int
    title: str
    content: str

    @classmethod
    def from_model(cls, note: Note) -> "NoteResponse":
        return cls(id=note.id, title=note.title, content=note.content)


@router.get("", response_model=list[NoteResponse])
async def list_notes() -> list[NoteResponse]:
    return [NoteResponse.from_model(note) for note in notes_service.list_notes()]


@router.post("", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
async def create_note(payload: NoteCreate) -> NoteResponse:
    note = notes_service.create(title=payload.title, content=payload.content)
    return NoteResponse.from_model(note)


@router.get("/{note_id}", response_model=NoteResponse)
async def get_note(note_id: int) -> NoteResponse:
    if note := notes_service.get(note_id):
        return NoteResponse.from_model(note)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(note_id: int) -> None:
    if not notes_service.delete(note_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
