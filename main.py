from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Optional
import os
from datetime import datetime
import json

from .models import ComplaintRequest, ClassificationResponse, Complaint
from .services import ClassificationService
from .database import ComplaintDatabase

app = FastAPI(title="SECP Complaints Classification System")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Initialize services
classification_service = ClassificationService()
db = ComplaintDatabase()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page with complaint form"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Dashboard page showing complaint history"""
    complaints = await db.get_complaints()
    stats = await db.get_stats()
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "complaints": complaints,
        "stats": stats
    })

@app.post("/api/classify")
async def classify_complaint(complaint: ComplaintRequest):
    """API endpoint for complaint classification"""
    try:
        result = await classification_service.classify(complaint.complaint_text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/submit-complaint")
async def submit_complaint(
    request: Request,
    complaint_text: str = Form(...),
    category: str = Form(...),
    subcategory: str = Form(...),
    nature_of_issue: str = Form(...)
):
    """Submit a complaint after classification"""
    try:
        # Create complaint record
        complaint = Complaint(
            text=complaint_text,
            category=category,
            subcategory=subcategory,
            nature_of_issue=nature_of_issue,
            timestamp=datetime.now(),
            status="classified"
        )
        
        # Save to database
        await db.save_complaint(complaint)
        
        return RedirectResponse(url="/dashboard?success=true", status_code=303)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/categories")
async def get_categories():
    """Get available complaint categories"""
    categories = {
        'Insurance Services': {
            'subcategories': ['Health Insurance Claims', 'Life Insurance Claims', 'Motor Insurance Claims', 'Property Insurance Claims'],
            'nature_of_issues': ['Delayed Processing', 'Claim Rejection', 'Premium Issues', 'Policy Terms Dispute']
        },
        'Brokerage Services': {
            'subcategories': ['Unauthorized Trading', 'Account Management', 'Commission Disputes', 'Market Manipulation'],
            'nature_of_issues': ['Account Manipulation', 'Excessive Charges', 'Poor Service Quality', 'Regulatory Violations']
        },
        'Investment Services': {
            'subcategories': ['Mutual Funds', 'Securities Trading', 'Portfolio Management', 'Investment Advisory'],
            'nature_of_issues': ['Performance Issues', 'Misleading Information', 'Unauthorized Transactions', 'Fee Disputes']
        },
        'Pension Services': {
            'subcategories': ['Retirement Benefits', 'Provident Fund', 'Gratuity Claims', 'Pension Payments'],
            'nature_of_issues': ['Withdrawal Process', 'Calculation Errors', 'Delayed Payments', 'Documentation Issues']
        },
        'Banking Services': {
            'subcategories': ['Loan Services', 'Account Services', 'Credit Cards', 'Digital Banking'],
            'nature_of_issues': ['Interest Rate Dispute', 'Service Charges', 'Account Access Issues', 'Transaction Disputes']
        },
        'Capital Markets': {
            'subcategories': ['Stock Exchange', 'Bond Markets', 'Derivatives', 'Market Infrastructure'],
            'nature_of_issues': ['Trading Issues', 'Settlement Problems', 'Market Data Issues', 'Regulatory Compliance']
        }
    }
    return categories

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)