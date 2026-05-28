"""
ICC API — Country lookup routes.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from api.models import CountryResponse, CountryListResponse, StatsResponse
from icc.core import (
    get_country_by_icc,
    get_country_by_iso,
    list_all_countries,
    search_countries,
    get_countries_by_continent,
    get_continents,
    get_statistics,
)
from icc.exceptions import InvalidICCCode, CountryNotFound

router = APIRouter(prefix="/countries", tags=["Countries"])


@router.get("", response_model=CountryListResponse, summary="List all countries")
def list_countries(
    limit: int = Query(default=50, ge=1, le=195, description="Max results"),
    offset: int = Query(default=0, ge=0, description="Offset for pagination"),
):
    """List all countries with their ICC codes, paginated."""
    all_countries = list_all_countries()
    subset = all_countries[offset : offset + limit]
    return CountryListResponse(total=len(all_countries), countries=subset)


@router.get("/stats", response_model=StatsResponse, summary="Get statistics")
def stats():
    """Get summary statistics about the ICC code system."""
    return get_statistics()


@router.get("/continents", summary="List continents")
def continents():
    """Get a list of all continents."""
    return {"continents": get_continents()}


@router.get(
    "/search",
    response_model=CountryListResponse,
    summary="Search countries",
)
def search(q: str = Query(..., min_length=1, description="Search query")):
    """Search countries by partial name, ISO code, or ICC code."""
    results = search_countries(q)
    return CountryListResponse(total=len(results), countries=results)


@router.get(
    "/continent/{continent_name}",
    response_model=CountryListResponse,
    summary="Filter by continent",
)
def by_continent(continent_name: str):
    """Get all countries in a given continent."""
    results = get_countries_by_continent(continent_name)
    if not results:
        raise HTTPException(status_code=404, detail=f"No countries found for continent: {continent_name}")
    return CountryListResponse(total=len(results), countries=results)


@router.get(
    "/iso/{iso_code}",
    response_model=CountryResponse,
    summary="Lookup by ISO code",
)
def by_iso(iso_code: str):
    """Look up a country by ISO 3166-1 alpha-2 or alpha-3 code."""
    try:
        return get_country_by_iso(iso_code)
    except CountryNotFound:
        raise HTTPException(status_code=404, detail=f"Country not found for ISO code: {iso_code}")


@router.get(
    "/{icc_code}",
    response_model=CountryResponse,
    summary="Lookup by ICC code",
)
def by_icc(icc_code: int):
    """Look up a country by its 3-digit ICC code."""
    try:
        return get_country_by_icc(icc_code)
    except InvalidICCCode:
        raise HTTPException(status_code=404, detail=f"No country assigned to ICC code: {icc_code}")
