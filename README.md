# Sunbeam Samanvay 1.0 (Ace One National Conclave)

Official Production Platform for **Sunbeam Samanvay 1.0** — The Annual Youth Parliament & Model United Nations Conference hosted by **Sunbeam Academy, Samneghat, Varanasi**.

---

## 🌟 Core Highlights
* **Name & Identity:** Sunbeam Samanvay 1.0 / Ace One National Conclave
* **Motto:** *"Speak. Shape. Solve."*
* **Core Philosophy:** *"Disagreement is where dialogue begins."* · *"Bring your strongest argument, not your loudest voice."*
* **Event Dates:** **23rd & 24th January 2027**
* **Host Campus:** Sunbeam Academy, Samneghat, Varanasi (Estd. 1972 / 1998)
* **Scale:** 700+ National Delegates across School & College divisions
* **Prize Pool:** **₹1,60,000 Total Cash Prizes** (₹20,000 cash pool per committee + mementos & certificates)

---

## 🌿 Design System & Aesthetics
* **Color Palette:** **Green & White** (Obsidian Forest `#064e3b`, Deep Pine `#022c22`, Rich Emerald `#059669`, Jade `#10b981`, Mint Light `#d1fae5`, Pure Crisp White `#ffffff`, and Champagne Gold `#d97706`).
* **Wavy Motion & Visuals:**
  * Interactive HTML5 Canvas sine-wave flow rendered dynamically in the hero background.
  * Multi-tiered organic SVG wave dividers connecting all sections.
  * Wavy pill badges, soft glassmorphism cards (`backdrop-blur-md`), and fluid floating micro-animations.

---

## 🏛️ The 8 Simulated Chambers & Agendas
1. **Lok Sabha (Indian Youth Parliament · Open for all):**
   * *Agenda:* Foreign Contribution (Regulation) Amendment Bill, 2026: Balancing National Security, State-Control Over Foreign Funded Assets and Contribution.
2. **AIPPM (All India Political Parties Meet · Open for all):**
   * *Agenda:* Framework of national electorate reforms, simultaneous polls ("One Nation, One Election") and the regulation of legal campaigning / AI deepfakes in elections.
3. **UPLA (Uttar Pradesh Legislative Assembly · Open for all):**
   * *Agenda:* State's employment generation strategy, public recruitment examination transparency, and youth migration management.
4. **Janmanch (Junior Assembly · Classes VI to X):**
   * *Agenda:* Deliberation on reforms in school education with special reference in practical learning, skill development, and education under NEP 2020.
5. **UNHRC (UN Human Rights Council · Open for all):**
   * *Agenda:* Safeguarding human rights and privacy in the agenda of widespread state-sponsored digital surveillance and biometric tracking.
6. **UNCSW (UN Commission on the Status of Women · Classes VI to X):**
   * *Agenda:* Accelerating women's economic empowerment and legal reforms to bridge leadership gaps in post-industrial workforce.
7. **UNGA (UN General Assembly · Open for all):**
   * *Agenda:* Reforming global multilateral institutions and governance framework to address escalating geopolitical fragmentation.
8. **IIP (International Indian Press · Open for all):**
   * *Agenda:* Assessing state mandate media blackouts and the state silencing of journalism under the guise of national security.

---

## 👥 Advisory Board & Core Leadership
* **Advisory Committee:**
  * **Mr. Rohan Madhok** – CEO, Sunbeam Academy, Samneghat
  * **Mrs. Shashwati Sharma** – Principal, Sunbeam Academy, Samneghat
  * **Miss Pratiksha Shahi** – Chief Advisor (BHU Alumna, 2x State Gold Medalist, Founder Vasant Vaani Sansad)
* **Core Organizers:**
  * **Ashwani Kumar Mishra** – Founder & Convenor
  * **Stuti Singh** – Co-Founder & Delegate Affairs
  * **Udita Singh** – Co-Founder & Logistics Head

---

## 🚀 Technical Architecture

### 1. Robust Backend (`server.py`)
Built on **FastAPI** with an embedded **SQLite** relational database (`samanvay.db`):
* `POST /api/registrations`: Registers delegates, validates inputs, assigns unique ticket IDs (e.g. `SAM-2027-1082`).
* `GET /api/registrations/{ticket_id}`: Verification lookup for delegate entry badges.
* `GET /api/committees`: Returns metadata, formal agendas, eligibility, and prize matrix for all 8 chambers.
* `GET /api/stats`: Real-time statistics (total registrations, slots remaining, committee breakdown).
* `POST /api/contact`: Collects official delegate inquiries.
* `GET /api/admin/registrations`: Protected secretariat endpoint with live search, filters, and status toggle.
* `GET /api/admin/export`: Instant 1-click CSV export of all registrations.
* `GET /brochure`: Direct 1-click download of the official 13-page `Event Brochure.pdf`.

### 2. Frontend (`public/index.html`)
* Responsive, fluid, single-page application.
* Real-time UPI QR payment integration (`stuti34@ptyes`).
* Interactive committee filter and deep-dive modals.
* Interactive photo gallery with category filtering and fullscreen Lightbox.
* Live countdown timer to January 23, 2027, 09:00 AM IST.

---

## 💻 How to Run

1. Open PowerShell or Terminal in `c:\Users\abhi's pc\Downloads\event.ace`.
2. Run:
```bash
python -m uvicorn server:app --host 0.0.0.0 --port 8000 --reload
```
or double-click `start.bat`.
3. Open your browser and navigate to:
   * **Website:** `http://localhost:8000`
   * **API Docs (Swagger UI):** `http://localhost:8000/docs`
