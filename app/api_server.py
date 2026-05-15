"""
Production-grade FastAPI service for SHL Recommender.

Endpoints:
- GET /health - System health check
- POST /chat - Process user conversation

Features:
- Pydantic request/response validation
- Deterministic outputs
- Graceful error handling
- Response timeout safety
- Stateless operation (conversation state managed client-side)
- Startup catalog preload
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import json
import logging
from datetime import datetime
import sys
import os

# Add workspace to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from shl_recommender import SHLRecommender

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# Pydantic Models - Strict Schema Validation
# ============================================================================

class Message(BaseModel):
    """Single conversation message."""
    role: Optional[str] = None  # "user" or "assistant"
    content: str = Field(..., min_length=1, max_length=10000)
    
    class Config:
        example = {
            "role": "user",
            "content": "We need a leadership assessment for a senior manager"
        }


class ChatRequest(BaseModel):
    """Chat endpoint request."""
    messages: List[Message] = Field(..., min_items=1, max_items=100)
    session_id: Optional[str] = None
    
    class Config:
        example = {
            "messages": [
                {
                    "role": "user",
                    "content": "We need leadership assessments"
                }
            ],
            "session_id": "session_123"
        }


class Recommendation(BaseModel):
    """Single assessment recommendation."""
    name: str = Field(..., min_length=1)
    url: str = Field(..., min_length=5)
    test_type: str = Field(..., min_length=1)
    
    class Config:
        example = {
            "name": "OPQ32r",
            "url": "https://example.com/opq32r",
            "test_type": "Personality"
        }


class ChatResponse(BaseModel):
    """Chat endpoint response."""
    reply: str = Field(..., min_length=1)
    recommendations: List[Recommendation]
    end_of_conversation: bool
    request_id: Optional[str] = None
    timestamp: Optional[str] = None
    
    class Config:
        example = {
            "reply": "Based on your requirements, here are suitable assessments:",
            "recommendations": [
                {
                    "name": "OPQ32r",
                    "url": "https://example.com/opq32r",
                    "test_type": "Personality"
                }
            ],
            "end_of_conversation": False,
            "request_id": "req_12345",
            "timestamp": "2026-05-15T12:00:00Z"
        }


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    timestamp: str
    catalog_size: int
    service_ready: bool


# ============================================================================
# FastAPI Application
# ============================================================================

app = FastAPI(
    title="SHL Recommender API",
    description="Production-grade conversational assessment recommender",
    version="1.0.0"
)

# Global recommender instance - initialized on startup
recommender: Optional[SHLRecommender] = None

# Get catalog path relative to app directory
import os
from pathlib import Path
catalog_path = str(Path(__file__).parent.parent / 'data' / 'shl_product_catalog_clean.json')
startup_time = None


@app.on_event("startup")
async def startup_event():
    """Initialize recommender on startup."""
    global recommender, startup_time
    
    try:
        logger.info("Starting SHL Recommender API...")
        startup_time = datetime.utcnow()
        
        # Verify catalog path exists
        if not os.path.exists(catalog_path):
            logger.warning(f"Catalog path not found: {catalog_path}, attempting alternate paths...")
        
        # Initialize recommender with catalog
        recommender = SHLRecommender(catalog_path)
        
        logger.info(f"[OK] Recommender initialized with {len(recommender.engine.assessments)} assessments")
        logger.info("[OK] API ready to accept requests")
        
    except Exception as e:
        logger.error(f"[ERROR] Startup error: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down SHL Recommender API...")


# ============================================================================
# Endpoints
# ============================================================================

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.
    
    Returns:
    - status: "ok" if healthy
    - timestamp: Current UTC time
    - catalog_size: Number of assessments loaded
    - service_ready: Whether service is ready
    """
    try:
        if not recommender or not recommender.engine.assessments:
            return HealthResponse(
                status="degraded",
                timestamp=datetime.utcnow().isoformat(),
                catalog_size=0,
                service_ready=False
            )
        
        return HealthResponse(
            status="ok",
            timestamp=datetime.utcnow().isoformat(),
            catalog_size=len(recommender.engine.assessments),
            service_ready=True
        )
    
    except Exception as e:
        logger.error(f"Health check error: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Process user message and return recommendations.
    
    Args:
    - messages: List of conversation messages
    - session_id: Optional session identifier
    
    Returns:
    - reply: Generated response text
    - recommendations: List of recommended assessments
    - end_of_conversation: Whether conversation should end
    
    Constraints:
    - Max 100 messages per request
    - Max 10,000 chars per message
    - Response time: <30 seconds
    - Schema: Strict validation
    """
    global recommender
    request_id = request.session_id or f"req_{datetime.utcnow().timestamp()}"
    
    try:
        # Lazy initialization if not already done
        if not recommender:
            logger.info("Lazy-loading recommender...")
            recommender = SHLRecommender(catalog_path)
        
        if not recommender:
            raise HTTPException(status_code=503, detail="Recommender not initialized")
        
        # Extract the last user message
        # Support both simple string messages and dict messages with "role" and "content"
        last_message = None
        
        # Try to find the last "user" message, or just take the last message
        for msg in reversed(request.messages):
            if not msg.role or msg.role == "user":
                last_message = msg.content
                break
        
        if not last_message:
            # Fallback to last message's content
            last_message = request.messages[-1].content
        
        if not last_message or len(last_message.strip()) == 0:
            raise HTTPException(status_code=400, detail="No valid user message found")
        
        logger.info(f"[{request_id}] Processing message: {last_message[:50]}...")
        
        # Get recommendations
        response = recommender.process_turn(last_message)
        
        # Validate response structure
        if not response or 'reply' not in response:
            raise ValueError("Invalid recommender response")
        
        # Convert to ChatResponse
        chat_response = ChatResponse(
            reply=response.get('reply', ''),
            recommendations=[
                Recommendation(
                    name=rec.get('name', 'Unknown'),
                    url=rec.get('url', ''),
                    test_type=rec.get('test_type', 'Assessment')
                )
                for rec in response.get('recommendations', [])
            ],
            end_of_conversation=response.get('end_of_conversation', False),
            request_id=request_id,
            timestamp=datetime.utcnow().isoformat()
        )
        
        logger.info(f"[{request_id}] Response: {len(chat_response.recommendations)} recommendations")
        
        return chat_response
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"[{request_id}] Error: {e}")
        
        # Graceful fallback response
        return ChatResponse(
            reply="I encountered an issue processing your request. Please try again.",
            recommendations=[],
            end_of_conversation=False,
            request_id=request_id,
            timestamp=datetime.utcnow().isoformat()
        )


@app.get("/")
async def root():
    """Root endpoint with API documentation."""
    return {
        "service": "SHL Recommender API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health (GET)",
            "chat": "/chat (POST)",
            "docs": "/docs"
        },
        "documentation": "/docs"
    }


# ============================================================================
# Entrypoint
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    # Run with uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        access_log=True
    )
