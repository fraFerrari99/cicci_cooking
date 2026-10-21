"""Schemi condivisi da tutte le API."""

from pydantic import BaseModel, Field


class ErrorBody(BaseModel):
    code: str = Field(description="Codice macchina, stabile, es. `not_found`, `validation_error`")
    message: str = Field(description="Messaggio leggibile, pensato per l'utente finale")
    details: object | None = Field(
        default=None, description="Dettagli opzionali (es. errori di validazione)"
    )
    request_id: str | None = Field(
        default=None, description="Id della richiesta, da citare nei bug report"
    )


class ErrorResponse(BaseModel):
    """Forma unica di ogni risposta di errore dell'API."""

    error: ErrorBody
