from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timedelta
import json


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI(title="Bypass Paywalls Clean - Backend", version="1.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Models for Bypass Extension
class BypassLog(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    action: str  # 'header_modified', 'cookies_cleared', 'paywall_detected', etc.
    domain: str
    url: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    user_agent: Optional[str] = None
    success: bool = True

class BypassLogCreate(BaseModel):
    action: str
    domain: str
    url: str
    user_agent: Optional[str] = None
    success: bool = True

class SiteConfig(BaseModel):
    domain: str
    name: str
    enabled: bool = True
    methods: Dict[str, Any]
    notes: Optional[str] = None
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class BypassStats(BaseModel):
    total_bypasses: int
    bypasses_today: int
    bypasses_this_week: int
    most_bypassed_sites: List[Dict[str, Any]]
    success_rate: float

class UpdateRulesResponse(BaseModel):
    success: bool
    message: str
    updated_sites: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# Legacy models (keeping for compatibility)
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str


# Bypass Extension Routes
@api_router.post("/bypass-log", response_model=BypassLog)
async def log_bypass_action(log_data: BypassLogCreate):
    """Log bypass actions from the Chrome extension"""
    log_dict = log_data.dict()
    log_obj = BypassLog(**log_dict)
    
    try:
        await db.bypass_logs.insert_one(log_obj.dict())
        return log_obj
    except Exception as e:
        logging.error(f"Failed to log bypass action: {e}")
        raise HTTPException(status_code=500, detail="Failed to log action")

@api_router.get("/bypass-stats", response_model=BypassStats)
async def get_bypass_stats():
    """Get bypass statistics for the extension popup"""
    try:
        # Get total bypasses
        total_bypasses = await db.bypass_logs.count_documents({})
        
        # Get today's bypasses
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        bypasses_today = await db.bypass_logs.count_documents({
            "timestamp": {"$gte": today_start}
        })
        
        # Get this week's bypasses
        week_start = today_start - timedelta(days=today_start.weekday())
        bypasses_this_week = await db.bypass_logs.count_documents({
            "timestamp": {"$gte": week_start}
        })
        
        # Get most bypassed sites
        pipeline = [
            {"$group": {"_id": "$domain", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 5}
        ]
        most_bypassed_cursor = db.bypass_logs.aggregate(pipeline)
        most_bypassed_sites = []
        async for doc in most_bypassed_cursor:
            most_bypassed_sites.append({
                "domain": doc["_id"],
                "count": doc["count"]
            })
        
        # Calculate success rate
        successful_bypasses = await db.bypass_logs.count_documents({"success": True})
        success_rate = (successful_bypasses / total_bypasses * 100) if total_bypasses > 0 else 0
        
        return BypassStats(
            total_bypasses=total_bypasses,
            bypasses_today=bypasses_today,
            bypasses_this_week=bypasses_this_week,
            most_bypassed_sites=most_bypassed_sites,
            success_rate=round(success_rate, 2)
        )
    except Exception as e:
        logging.error(f"Failed to get bypass stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get statistics")

@api_router.get("/site-config/{domain}")
async def get_site_config(domain: str):
    """Get configuration for a specific site"""
    try:
        config = await db.site_configs.find_one({"domain": domain})
        if config:
            return config
        else:
            # Return default config for lefigaro.fr or None for unsupported sites
            if domain == "lefigaro.fr":
                return {
                    "domain": "lefigaro.fr",
                    "name": "Le Figaro",
                    "enabled": True,
                    "methods": {
                        "removeCookies": ["PHPSESSID", "_ga", "_gid", "tarteaucitron"],
                        "useragent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
                        "referer": "https://www.google.com/",
                        "techniques": ["cookies", "useragent", "referer", "archive"]
                    }
                }
            return None
    except Exception as e:
        logging.error(f"Failed to get site config: {e}")
        raise HTTPException(status_code=500, detail="Failed to get site configuration")

@api_router.post("/update-rules", response_model=UpdateRulesResponse)
async def update_bypass_rules():
    """Update bypass rules and site configurations"""
    try:
        # In a real implementation, this would fetch updated rules from a remote source
        # For now, we'll just update the timestamp and return success
        
        # Update Le Figaro configuration
        lefigaro_config = {
            "domain": "lefigaro.fr",
            "name": "Le Figaro",
            "enabled": True,
            "methods": {
                "removeCookies": ["PHPSESSID", "_ga", "_gid", "tarteaucitron", "figaro_paywall", "premium_views"],
                "removePaywallSelectors": [
                    ".fig-paywall",
                    ".fig-premium-paywall",
                    ".subscription-banner",
                    "[class*='paywall']"
                ],
                "useragent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
                "referer": "https://www.google.com/",
                "techniques": ["cookies", "useragent", "referer", "dom_manipulation", "archive"]
            },
            "notes": "Support complet avec extraction JSON-LD et redirection archive",
            "last_updated": datetime.utcnow()
        }
        
        await db.site_configs.replace_one(
            {"domain": "lefigaro.fr"},
            lefigaro_config,
            upsert=True
        )
        
        return UpdateRulesResponse(
            success=True,
            message="Règles mises à jour avec succès",
            updated_sites=1
        )
    except Exception as e:
        logging.error(f"Failed to update rules: {e}")
        raise HTTPException(status_code=500, detail="Failed to update rules")

@api_router.get("/supported-sites")
async def get_supported_sites():
    """Get list of all supported sites"""
    try:
        sites = await db.site_configs.find({}).to_list(100)
        return sites
    except Exception as e:
        logging.error(f"Failed to get supported sites: {e}")
        raise HTTPException(status_code=500, detail="Failed to get supported sites")

@api_router.post("/test-bypass")
async def test_bypass(url: str):
    """Test bypass functionality for a given URL"""
    try:
        from urllib.parse import urlparse
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.replace('www.', '')
        
        # Log the test
        test_log = BypassLogCreate(
            action="test_bypass",
            domain=domain,
            url=url,
            success=True
        )
        
        log_obj = BypassLog(**test_log.dict())
        await db.bypass_logs.insert_one(log_obj.dict())
        
        return {
            "success": True,
            "domain": domain,
            "supported": domain == "lefigaro.fr",
            "message": f"Test effectué pour {domain}"
        }
    except Exception as e:
        logging.error(f"Failed to test bypass: {e}")
        raise HTTPException(status_code=500, detail="Failed to test bypass")

# Legacy routes (keeping for compatibility)
@api_router.get("/")
async def root():
    return {
        "message": "Bypass Paywalls Clean - Backend API",
        "version": "1.0.0",
        "endpoints": {
            "bypass-log": "POST - Log bypass actions",
            "bypass-stats": "GET - Get bypass statistics",
            "site-config/{domain}": "GET - Get site configuration",
            "update-rules": "POST - Update bypass rules",
            "supported-sites": "GET - Get supported sites list",
            "test-bypass": "POST - Test bypass for URL"
        }
    }

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    _ = await db.status_checks.insert_one(status_obj.dict())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
