from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from app.services.orchestration.search_orchestration import SearchOrchestrator
from app.schemas.search import SearchQuery, SearchResponse
from fastapi import Request, HTTPException
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter

# Create FastAPI instance
app = FastAPI(
    title="PrecedentAI API",
    description="AI-powered precedent analysis API",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

search_orchestrator = SearchOrchestrator()


@app.get("/")
async def root():
    return {"message": "Welcome to the PrecedentAI API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/search", response_model=SearchResponse)
@limiter.limit("5/hour")  # Allow 5 requests per hour per IP
async def search_papers(request: Request, query: SearchQuery):
    """
    Search endpoint that combines academic papers and web results
    """
    try:
        search_response = await search_orchestrator.search(query.query)
        return search_response
    
    except HTTPException as exception:
        raise exception
    except Exception as e:
        print(f"Search error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your search"
        )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )