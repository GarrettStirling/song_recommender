from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from app.api import auth, spotify_data, recommendations
from app.services.spotify_service import SpotifyService
import os
import sys
# Ensure the app directory is in the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

# Create FastAPI instance
app = FastAPI(
    title="Spotify Recommender API",
    description="AI-powered music recommendations based on your Spotify profile",
    version="1.0.0"
)

# Add CORS middleware (for frontend communication)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server (React frontend)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(spotify_data.router)
app.include_router(recommendations.router)

@app.get("/")
async def root():
    return {"message": "Spotify Recommender API is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

@app.get("/callback")
async def fallback_callback(code: str = Query(...), state: str = Query(None)):
    """Fallback callback for Spotify OAuth - redirects to proper auth callback"""
    try:
        # Initialize Spotify service
        spotify_service = SpotifyService()
        
        # Exchange code for access token
        token_info = spotify_service.get_access_token(code)
        
        if not token_info:
            raise HTTPException(status_code=400, detail="Failed to get access token")
        
        # Return token info
        return {
            "access_token": token_info['access_token'],
            "refresh_token": token_info['refresh_token'],
            "expires_in": token_info['expires_in'],
            "message": "Authentication successful! (via fallback route)"
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Callback error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)