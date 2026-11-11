"""
Sunbeam Samanvay 1.0 (Ace One National Conclave) - Production Backend Server
Powered by FastAPI, SQLite, Pydantic
"""

import os
import sqlite3
import random
import string
from datetime import datetime
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Depends, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel, EmailStr, Field
import io
import csv

DB_PATH = "samanvay.db"

app = FastAPI(
    title="Sunbeam Samanvay 1.0 API",
    description="Backend API for Sunbeam Samanvay 1.0 (Ace One National Youth Parliament & MUN)",
    version="1.0.0"
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------- Database Setup -----------------
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    # Registrations table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS registrations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticket_id TEXT UNIQUE NOT NULL,
        full_name TEXT NOT NULL,
        email TEXT NOT NULL,
        phone TEXT NOT NULL,
        institution TEXT NOT NULL,
        education_level TEXT NOT NULL,
        committee_pref_1 TEXT NOT NULL,
        committee_pref_2 TEXT,
        portfolio_pref TEXT,
        prior_experience TEXT,
        needs_accommodation INTEGER DEFAULT 0,
        emergency_contact TEXT,
        transaction_id TEXT,
        amount_paid INTEGER DEFAULT 999,
        payment_status TEXT DEFAULT 'CONFIRMED',
        created_at TEXT NOT NULL
    )
    """)
    
    # Contact messages table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS contact_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        phone TEXT,
        subject TEXT NOT NULL,
        message TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    """)
    
    # Seed initial realistic delegates if empty
    cursor.execute("SELECT COUNT(*) as cnt FROM registrations")
    count = cursor.fetchone()["cnt"]
    if count == 0:
        sample_delegates = [
            ("SAM-2027-1001", "Aarav Sharma", "aarav.sharma@gmail.com", "+91 98765 43210", "Delhi Public School, Varanasi", "Senior Secondary (XI-XII)", "LOK_SABHA", "AIPPM", "Minister of Home Affairs", "2 MUNs", 0, "+91 98765 43211", "UPI-UTR-908214309", 999, "CONFIRMED", "2026-11-01 10:15:00"),
            ("SAM-2027-1002", "Ananya Verma", "ananya.v@bhu.ac.in", "+91 91234 56789", "Banaras Hindu University (BHU)", "Undergraduate", "UNHRC", "UNGA", "Delegate of France", "5+ MUNs", 0, "+91 91234 56780", "UPI-UTR-718293041", 999, "CONFIRMED", "2026-11-02 14:22:10"),
            ("SAM-2027-1003", "Rohan Kulkarni", "rohan.k@iitbhu.ac.in", "+91 94561 23789", "IIT (BHU) Varanasi", "Undergraduate", "AIPPM", "LOK_SABHA", "Leader of Opposition", "3 MUNs", 0, "+91 94561 23780", "UPI-UTR-891234710", 999, "CONFIRMED", "2026-11-04 09:45:30"),
            ("SAM-2027-1004", "Isha Mukherjee", "isha.m@sunbeam.edu.in", "+91 98321 45678", "Sunbeam Academy, Samneghat", "High School (IX-X)", "JANMANCH", "UNCSW", "Education Reform Advocate", "1 MUN", 0, "+91 98321 45670", "UPI-UTR-349012871", 999, "CONFIRMED", "2026-11-06 16:30:15"),
            ("SAM-2027-1005", "Devendra Pratap Singh", "devendra.singh@gmail.com", "+91 97890 12345", "Lucknow University", "Undergraduate", "UPLA", "LOK_SABHA", "Chief Minister UP", "4 MUNs", 1, "+91 97890 12340", "UPI-UTR-561239082", 999, "CONFIRMED", "2026-11-08 11:10:45"),
            ("SAM-2027-1006", "Sanya Kapoor", "sanya.k@modernschool.com", "+91 99887 76655", "The Modern School, Lucknow", "Senior Secondary (XI-XII)", "UNCSW", "UNHRC", "Delegate of Sweden", "2 MUNs", 1, "+91 99887 76650", "UPI-UTR-102938475", 999, "CONFIRMED", "2026-11-10 13:05:20"),
            ("SAM-2027-1007", "Kavya Tripathi", "kavya.tripathi@gmail.com", "+91 93456 78120", "St. John's Academy", "High School (IX-X)", "IIP", "JANMANCH", "Senior Photojournalist", "First Timer", 0, "+91 93456 78129", "UPI-UTR-657483920", 999, "CONFIRMED", "2026-11-11 08:40:00")
        ]
        cursor.executemany("""
        INSERT INTO registrations (ticket_id, full_name, email, phone, institution, education_level, committee_pref_1, committee_pref_2, portfolio_pref, prior_experience, needs_accommodation, emergency_contact, transaction_id, amount_paid, payment_status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, sample_delegates)
        
    conn.commit()
    conn.close()

init_db()

# ----------------- Data Models -----------------
class RegistrationRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., min_length=5, max_length=100)
    phone: str = Field(..., min_length=10, max_length=15)
    institution: str = Field(..., min_length=2, max_length=150)
    education_level: str
    committee_pref_1: str
    committee_pref_2: Optional[str] = None
    portfolio_pref: Optional[str] = None
    prior_experience: Optional[str] = "Beginner"
    needs_accommodation: Optional[bool] = False
    emergency_contact: Optional[str] = None
    transaction_id: str = Field(..., min_length=4, max_length=50)
    amount_paid: Optional[int] = 999

class ContactRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., min_length=5, max_length=100)
    phone: Optional[str] = None
    subject: str = Field(..., min_length=3, max_length=150)
    message: str = Field(..., min_length=10, max_length=2000)

class StatusUpdateRequest(BaseModel):
    payment_status: str

# ----------------- Committees Data -----------------
COMMITTEES_DATA = [
    {
        "id": "lok-sabha",
        "key": "LOK_SABHA",
        "name": "Lok Sabha",
        "category": "Youth Parliament",
        "forum": "Indian Youth Parliament",
        "eligibility": "Open for all (School & College)",
        "tagline": "The Lower House of the Indian Parliament",
        "logo": "/assets/committees/lok_sabha.jpg",
        "agenda": "Foreign Contribution (Regulation) Amendment Bill, 2026: Balancing National Security, State-Control Over Foreign Funded Assets and Contribution.",
        "description": "Step into the shoes of Members of Parliament representing sovereign India's diverse constituencies. Deliberate, debate constitutional clauses, and craft robust legislation on sovereign security and foreign funding.",
        "prizes": [
            {"title": "Best Parliamentarian", "amount": "₹10,000", "perk": "Trophy + Memento + Certificate of Excellence"},
            {"title": "High Commendation", "amount": "₹6,000", "perk": "Memento + Certificate of Merit"},
            {"title": "Special Mention", "amount": "₹3,000", "perk": "Certificate of Merit"},
            {"title": "Honourable Mention", "amount": "₹1,000", "perk": "Certificate of Merit"}
        ]
    },
    {
        "id": "aippm",
        "key": "AIPPM",
        "name": "All India Political Parties Meet",
        "category": "Youth Parliament",
        "forum": "Indian Youth Parliament",
        "eligibility": "Open for all (School & College)",
        "tagline": "Cross-Party Consensus & National Discourse",
        "logo": "/assets/committees/aippm.jpg",
        "agenda": "Discussion on the framework of national electorate reforms, simultaneous polls ('One Nation, One Election') and the regulation of legal campaigning / AI deepfakes in elections.",
        "description": "Brings together national party leaders across political spectrums. Deliberate contentious democratic electoral reforms, legislative restructuring, and technological guardrails.",
        "prizes": [
            {"title": "Best Leader", "amount": "₹10,000", "perk": "Trophy + Memento + Certificate of Excellence"},
            {"title": "High Commendation", "amount": "₹6,000", "perk": "Memento + Certificate of Merit"},
            {"title": "Special Mention", "amount": "₹3,000", "perk": "Certificate of Merit"},
            {"title": "Honourable Mention", "amount": "₹1,000", "perk": "Certificate of Merit"}
        ]
    },
    {
        "id": "upla",
        "key": "UPLA",
        "name": "Uttar Pradesh Legislative Assembly",
        "category": "Youth Parliament",
        "forum": "Indian Youth Parliament",
        "eligibility": "Open for all (School & College)",
        "tagline": "Vidhan Sabha — State Governance & Public Policy",
        "logo": "/assets/committees/upla.jpg",
        "agenda": "Deliberation on state's employment generation strategy, public recruitment examination transparency and youth migration management.",
        "description": "The floor of Uttar Pradesh's Vidhan Sabha tests the courage of legislators debating the state's largest challenges: government exam integrity, youth employment, and economic infrastructure.",
        "prizes": [
            {"title": "Best Legislator", "amount": "₹10,000", "perk": "Trophy + Memento + Certificate of Excellence"},
            {"title": "High Commendation", "amount": "₹6,000", "perk": "Memento + Certificate of Merit"},
            {"title": "Special Mention", "amount": "₹3,000", "perk": "Certificate of Merit"},
            {"title": "Honourable Mention", "amount": "₹1,000", "perk": "Certificate of Merit"}
        ]
    },
    {
        "id": "janmanch",
        "key": "JANMANCH",
        "name": "Janmanch (Junior Assembly)",
        "category": "Youth Parliament",
        "forum": "Indian Youth Parliament",
        "eligibility": "Classes VI to X (Junior Category)",
        "tagline": "The Voice of Emerging School Delegates",
        "logo": "/assets/committees/janmanch.jpg",
        "agenda": "Deliberation on reforms in school education with special reference in practical learning, skill development and education under NEP 2020.",
        "description": "A tailored forum exclusively designed for students from Class 6 to 10 to articulate ideas on student well-being, educational reforms, and skill-based curricula.",
        "prizes": [
            {"title": "Best Junior Speaker", "amount": "₹10,000", "perk": "Trophy + Memento + Certificate of Excellence"},
            {"title": "High Commendation", "amount": "₹6,000", "perk": "Memento + Certificate of Merit"},
            {"title": "Special Mention", "amount": "₹3,000", "perk": "Certificate of Merit"},
            {"title": "Honourable Mention", "amount": "₹1,000", "perk": "Certificate of Merit"}
        ]
    },
    {
        "id": "unhrc",
        "key": "UNHRC",
        "name": "UN Human Rights Council",
        "category": "MUN",
        "forum": "Model United Nations",
        "eligibility": "Open for all (School & College)",
        "tagline": "Dignity, Justice & Fundamental Freedoms",
        "logo": "/assets/committees/unhrc.jpg",
        "agenda": "Deliberation in safeguarding human rights and privacy in the agenda of widespread state sponsored digital surveillance and biometric tracking.",
        "description": "Diplomats address cutting-edge human rights violations in the digital era: state Pegasus spyware, biometric facial recognition surveillance, and digital personal liberty.",
        "prizes": [
            {"title": "Best Delegate", "amount": "₹10,000", "perk": "Trophy + Memento + Certificate of Excellence"},
            {"title": "High Commendation", "amount": "₹6,000", "perk": "Memento + Certificate of Merit"},
            {"title": "Special Mention", "amount": "₹3,000", "perk": "Certificate of Merit"},
            {"title": "Honourable Mention", "amount": "₹1,000", "perk": "Certificate of Merit"}
        ]
    },
    {
        "id": "uncsw",
        "key": "UNCSW",
        "name": "UN Commission on the Status of Women",
        "category": "MUN",
        "forum": "Model United Nations",
        "eligibility": "Classes VI to X (Junior Category)",
        "tagline": "Gender Equality, Leadership & Empowerment",
        "logo": "/assets/committees/uncsw.jpg",
        "agenda": "Discussion on accelerating women's economic empowerment and legal reforms to bridge leadership gaps in post-industrial workforce.",
        "description": "Focused committee for younger diplomats to craft resolutions empowering women in STEM, corporate boards, wage equality, and international labor legal rights.",
        "prizes": [
            {"title": "Best Delegate", "amount": "₹10,000", "perk": "Trophy + Memento + Certificate of Excellence"},
            {"title": "High Commendation", "amount": "₹6,000", "perk": "Memento + Certificate of Merit"},
            {"title": "Special Mention", "amount": "₹3,000", "perk": "Certificate of Merit"},
            {"title": "Honourable Mention", "amount": "₹1,000", "perk": "Certificate of Merit"}
        ]
    },
    {
        "id": "unga",
        "key": "UNGA",
        "name": "UN General Assembly",
        "category": "MUN",
        "forum": "Model United Nations",
        "eligibility": "Open for all (School & College)",
        "tagline": "Global Diplomacy & Multilateral Governance",
        "logo": "/assets/committees/unga.jpg",
        "agenda": "Deliberation on reforming global multilateral institutions and governance framework to address escalating geopolitical fragmentation.",
        "description": "The quintessential committee of global nations. Addressing UN Security Council veto reforms, multilateral treaty adherence, and international conflict resolution.",
        "prizes": [
            {"title": "Best Delegate", "amount": "₹10,000", "perk": "Trophy + Memento + Certificate of Excellence"},
            {"title": "High Commendation", "amount": "₹6,000", "perk": "Memento + Certificate of Merit"},
            {"title": "Special Mention", "amount": "₹3,000", "perk": "Certificate of Merit"},
            {"title": "Honourable Mention", "amount": "₹1,000", "perk": "Certificate of Merit"}
        ]
    },
    {
        "id": "iip",
        "key": "IIP",
        "name": "International Indian Press",
        "category": "MUN",
        "forum": "Model United Nations & Journalism",
        "eligibility": "Open for all (School & College)",
        "tagline": "The Fourth Pillar — Journalists & Chroniclers",
        "logo": "/assets/committees/iip.jpg",
        "agenda": "Assessing state mandated media blackouts and the state silencing of journalism under the guise of national security.",
        "description": "Reporters, investigative columnists, and photojournalists holding power accountable. Publish real-time conference gazettes, interview key diplomats, and document proceedings.",
        "prizes": [
            {"title": "Best Journalist", "amount": "₹10,000", "perk": "Trophy + Memento + Certificate of Excellence"},
            {"title": "High Commendation", "amount": "₹6,000", "perk": "Memento + Certificate of Merit"},
            {"title": "Special Mention", "amount": "₹3,000", "perk": "Certificate of Merit"},
            {"title": "Honourable Mention", "amount": "₹1,000", "perk": "Certificate of Merit"}
        ]
    }
]

# ----------------- API Endpoints -----------------

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "event": "Sunbeam Samanvay 1.0 (Ace One Conclave)",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/committees")
def get_committees():
    return {"committees": COMMITTEES_DATA}

@app.get("/api/stats")
def get_stats():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as total FROM registrations")
    total_reg = cursor.fetchone()["total"]
    
    cursor.execute("SELECT COUNT(*) as verified FROM registrations WHERE payment_status = 'CONFIRMED'")
    verified_reg = cursor.fetchone()["verified"]
    
    cursor.execute("SELECT committee_pref_1, COUNT(*) as count FROM registrations GROUP BY committee_pref_1")
    comm_counts = {row["committee_pref_1"]: row["count"] for row in cursor.fetchall()}
    
    conn.close()
    
    # Event Target: 700+
    base_display_count = 214 + total_reg
    return {
        "total_registrations": base_display_count,
        "verified_registrations": verified_reg,
        "capacity_target": 700,
        "slots_remaining": max(0, 700 - base_display_count),
        "total_prize_pool": "₹1,60,000+",
        "total_committees": 8,
        "early_bird_fee": 999,
        "regular_fee": 1199,
        "committee_breakdown": comm_counts
    }

@app.post("/api/registrations")
def create_registration(req: RegistrationRequest):
    conn = get_db()
    cursor = conn.cursor()
    
    # Generate unique ticket ID: SAM-2027-XXXX
    random_num = random.randint(1050, 9999)
    ticket_id = f"SAM-2027-{random_num}"
    
    # Check duplicate
    cursor.execute("SELECT id FROM registrations WHERE email = ? OR phone = ?", (req.email, req.phone))
    existing = cursor.fetchone()
    if existing:
        conn.close()
        raise HTTPException(status_code=400, detail="A registration with this email or phone number already exists!")
    
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        cursor.execute("""
        INSERT INTO registrations (
            ticket_id, full_name, email, phone, institution, education_level,
            committee_pref_1, committee_pref_2, portfolio_pref, prior_experience,
            needs_accommodation, emergency_contact, transaction_id, amount_paid,
            payment_status, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'CONFIRMED', ?)
        """, (
            ticket_id, req.full_name, req.email, req.phone, req.institution, req.education_level,
            req.committee_pref_1, req.committee_pref_2 or "", req.portfolio_pref or "", req.prior_experience or "Beginner",
            1 if req.needs_accommodation else 0, req.emergency_contact or "", req.transaction_id,
            req.amount_paid or 999, created_at
        ))
        conn.commit()
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        
    conn.close()
    
    return {
        "success": True,
        "message": "Registration successful! Welcome to Sunbeam Samanvay 1.0.",
        "ticket_id": ticket_id,
        "delegate_name": req.full_name,
        "committee": req.committee_pref_1,
        "amount_paid": req.amount_paid or 999,
        "created_at": created_at
    }

@app.get("/api/registrations/{ticket_id}")
def get_registration(ticket_id: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM registrations WHERE ticket_id = ?", (ticket_id.upper(),))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="Delegate credential ticket not found.")
        
    return dict(row)

@app.post("/api/contact")
def submit_contact_query(req: ContactRequest):
    conn = get_db()
    cursor = conn.cursor()
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
    INSERT INTO contact_messages (name, email, phone, subject, message, created_at)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (req.name, req.email, req.phone or "", req.subject, req.message, created_at))
    conn.commit()
    conn.close()
    return {
        "success": True,
        "message": "Your message has been received by the Secretariat. We will respond within 24 hours."
    }

# ----------------- Admin Endpoints -----------------

@app.get("/api/admin/registrations")
def list_registrations(search: Optional[str] = None, committee: Optional[str] = None):
    conn = get_db()
    cursor = conn.cursor()
    query = "SELECT * FROM registrations WHERE 1=1"
    params = []
    
    if committee and committee != "ALL":
        query += " AND committee_pref_1 = ?"
        params.append(committee)
        
    if search:
        query += " AND (full_name LIKE ? OR email LIKE ? OR institution LIKE ? OR ticket_id LIKE ?)"
        s = f"%{search}%"
        params.extend([s, s, s, s])
        
    query += " ORDER BY id DESC"
    cursor.execute(query, params)
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return {"registrations": rows, "count": len(rows)}

@app.patch("/api/admin/registrations/{reg_id}/status")
def update_status(reg_id: int, req: StatusUpdateRequest):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE registrations SET payment_status = ? WHERE id = ?", (req.payment_status, reg_id))
    conn.commit()
    conn.close()
    return {"success": True, "message": f"Registration #{reg_id} status updated to {req.payment_status}."}

@app.get("/api/admin/export")
def export_csv():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM registrations ORDER BY id ASC")
    rows = cursor.fetchall()
    conn.close()
    
    output = io.StringIO()
    writer = csv.writer(output)
    if rows:
        writer.writerow(rows[0].keys())
        for row in rows:
            writer.writerow(list(row))
    else:
        writer.writerow(["No registrations"])
        
    output.seek(0)
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=samanvay_registrations.csv"}
    )

# ----------------- Static Files & Mounts -----------------
# Ensure public directory exists
os.makedirs("public", exist_ok=True)
os.makedirs("public/assets", exist_ok=True)

app.mount("/assets", StaticFiles(directory="public/assets"), name="assets")

@app.get("/brochure")
def download_brochure():
    brochure_path = "public/assets/Sunbeam-Samanvay-Brochure.pdf"
    if os.path.exists(brochure_path):
        return FileResponse(
            brochure_path,
            filename="Sunbeam-Samanvay-1.0-Brochure.pdf",
            media_type="application/pdf"
        )
    raise HTTPException(status_code=404, detail="Brochure PDF not found.")

@app.get("/")
def serve_home():
    return FileResponse("public/index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
