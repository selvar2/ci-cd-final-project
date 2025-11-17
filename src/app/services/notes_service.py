from __future__ import annotations

from dataclasses import dataclass, field
from threading import Lock
from typing import Dict, List

from ..logging_config import get_logger
from ..storage import storage_client

logger = get_logger(__name__)


@dataclass
class Note:
    title: str
    content: str
    id: int = field(default=0)


class NotesService:
    """Simple note service with persistence via storage_client."""

    def __init__(self) -> None:
        self._lock = Lock()
        self._notes: Dict[int, Note] = {}
        self._sequence = 1
        self._load()

    def _load(self) -> None:
        data = storage_client.read_json("notes.json", default=[])
        for item in data:
            note = Note(**item)
            self._notes[note.id] = note
            self._sequence = max(self._sequence, note.id + 1)
        logger.info("Loaded %d notes from storage", len(self._notes))

    def _persist(self) -> None:
        payload = [note.__dict__ for note in self._notes.values()]
        storage_client.write_json("notes.json", payload)

    def list_notes(self) -> List[Note]:
        with self._lock:
            return list(self._notes.values())

    def create(self, title: str, content: str) -> Note:
        with self._lock:
            note = Note(id=self._sequence, title=title, content=content)
            self._notes[note.id] = note
            self._sequence += 1
            self._persist()
            logger.info("Created note %s", note.id, extra={"request_id": getattr(logger, "request_id", "-")})
            return note

    def get(self, note_id: int) -> Note | None:
        with self._lock:
            return self._notes.get(note_id)

    def delete(self, note_id: int) -> bool:
        with self._lock:
            if note_id in self._notes:
                del self._notes[note_id]
                self._persist()
                return True
            return False


notes_service = NotesService()
