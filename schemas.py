"""Schemas for data structures used in the taste.io scraper."""

from typing import TypedDict, List, Optional, Union

class SimklID(TypedDict):
    simkl: int

class MediaEntry(TypedDict):
    title: str
    rating: Optional[float]
    year: Union[str, int]
    to: str
    ids: SimklID

class SimklBackup(TypedDict):
    movies: List[MediaEntry]
    shows: List[MediaEntry]

class TasteIOItem(TypedDict):
    name: str
    starRating: Optional[float]
    lastReaction: Optional[int]
    year: Union[str, int]
    slug: str
    category: str
    user: dict