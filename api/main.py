"""
ICC API — FastAPI Application
Internet Calling Code REST API for VOIP and Blockchain integration.

Author: Mobyap (mobyap.com@gmail.com)
License: MIT

Run with: uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
Docs at:  http://localhost:8000/docs
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.routes import lookup, validate, voip, blockchain, isn, codes
from icc import __version__
from icc.core import get_statistics

app = FastAPI(
    title="ICC — Internet Calling Code API",
    description=(
        "REST API providing 3-digit Internet Communications Codes (ICC) for "
        "195 sovereign countries, with integration endpoints for VOIP systems "
        "and blockchain networks.\n\n"
        "**Author**: Mobyap (mobyap.com@gmail.com)\n\n"
        "## ICC Codes\n"
        "Codes are assigned based on country **land area** (largest → smallest) "
        "using a deterministic numbering sequence. Russia (largest) gets code 100.\n\n"
        "## ISN — Internet Subscriber Number\n"
        "Full subscriber numbers follow the format: `ICC-RRRR-SSSS-SSSS`\n"
        "- **ICC** (3 digits): Internet Calling Code\n"
        "- **RRRR** (4 digits): Region and Purpose Code\n"
        "- **SSSS-SSSS** (8 digits): Subscriber Number\n"
        "- Example: `100-1234-5678-0321`\n\n"
        "## Code Categories\n"
        "- **Country Codes**: 882 codes (100–999, excluding reserved)\n"
        "- **Special Codes**: 18 reserved codes for global services "
        "(education, emergency, military, etc.)\n"
        "- **App Codes**: 9 codes (010–090) for Mobyap blockchain VOIP\n\n"
        "## Integration\n"
        "- **VOIP**: SIP URI generation, E.164 mapping, dial strings, SIP headers\n"
        "- **Blockchain**: SHA-256 hashing, verification tokens, smart contract ABI, "
        "ABI encoding, Merkle proofs\n\n"
        "**License**: MIT — Free for commercial use."
    ),
    version=__version__,
    license_info={"name": "MIT", "url": "https://opensource.org/licenses/MIT"},
    contact={
        "name": "Mobyap",
        "email": "mobyap.com@gmail.com",
    },
)

# CORS — allow all origins for development / open API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Mount routes ─────────────────────────────────────────────────────────────

app.include_router(lookup.router, prefix="/api/v1")
app.include_router(validate.router, prefix="/api/v1")
app.include_router(voip.router, prefix="/api/v1")
app.include_router(blockchain.router, prefix="/api/v1")
app.include_router(isn.router, prefix="/api/v1")
app.include_router(codes.router, prefix="/api/v1")


# ── Root & health ────────────────────────────────────────────────────────────

@app.get("/", tags=["System"])
def root():
    """API root — returns basic info and links."""
    return {
        "name": "ICC — Internet Calling Code API",
        "version": __version__,
        "author": "Mobyap",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
        "api_base": "/api/v1",
    }


@app.get("/health", tags=["System"])
def health():
    """Health check endpoint."""
    stats = get_statistics()
    return {
        "status": "healthy",
        "version": __version__,
        "countries_loaded": stats["total_countries"],
        "codes_available": stats["total_country_codes_available"],
        "reserved_codes": stats["reserved_special_codes"],
        "app_codes": stats["app_codes"],
    }
