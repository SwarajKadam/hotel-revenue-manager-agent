# Hotel Revenue Manager Agent

An AI-powered hotel revenue management assistant that helps a hotel General Manager ask business questions about on-the-books revenue, ADR, OTA dependency, cancellations, pickup, room type performance, rate plans, financial status, and market mix.

The system scrapes reservation data from a JavaScript-rendered hotel data portal, loads the data into PostgreSQL, verifies the loaded dataset against the source portal, exposes trusted business metrics through FastAPI, and connects those metrics to an AI agent that answers hotel revenue questions in plain business language.

---

## Live Demo

The project is deployed with the frontend on Vercel and the backend on Render.

| Component        | Link                                                    |
| ---------------- | ------------------------------------------------------- |
| Frontend Demo    | https://hotel-revenue-manager-agent.vercel.app/         |
| Backend API Docs | https://hotel-revenue-manager-backend.onrender.com/docs |

A simple basic authentication layer is included on the frontend to restrict demo access. This is intentionally lightweight for demo purposes and does not use hidden URLs or a full production authentication system.

---

## Project Overview

Hotel revenue managers need to understand business performance across several dimensions:

* Monthly on-the-books revenue
* Room nights and ADR
* OTA dependency
* Channel mix
* Market segment mix
* Room type performance
* Rate plan performance
* Posted vs provisional revenue
* Group/block business
* Cancellations
* Recent booking pickup
* Dataset verification against the source portal

Instead of manually checking several reports, this project allows a user to ask natural language questions such as:

* What revenue is on the books by month?
* Are we too dependent on OTA?
* Which room type has the highest ADR?
* Which rate plan performs best?
* Show posted vs provisional revenue.
* What changed in the last 7 days?
* Which market segments are driving demand?
* Does my database match the source site?

The AI agent uses trusted backend tools and database metrics rather than inventing answers.

---

## Key Features

* Deployed React frontend on Vercel
* Deployed FastAPI backend on Render
* Simple frontend basic auth layer for demo access
* Playwright-based web scraping for JavaScript-rendered reservation data
* ETL pipeline to extract, clean, transform, and load reservation data
* One-row-per-reservation-stay-date database design
* PostgreSQL database support
* FastAPI backend with health, metrics, ETL, verification, and chat endpoints
* LangChain tool layer connected to verified business metrics
* AI revenue manager assistant for natural-language business questions
* React frontend for asking hotel business questions
* Markdown-rendered AI responses
* CORS-enabled frontend-backend communication
* Dataset verification using `/verify` page values
* Rate plan lookup support
* Macro group history support for stay-date-aware market classification
* Posted vs provisional revenue analysis
* Edge-case reservation ID support

---

## Architecture

```txt
Hotel Data Website
    ↓
Playwright Scraper
    ↓
ETL Transformation
    ↓
PostgreSQL Database
    ↓
FastAPI Metrics API
    ↓
LangChain Tools
    ↓
AI Revenue Manager Agent
    ↓
React Frontend
```

---

## Tech Stack

| Layer                  | Technology                         |
| ---------------------- | ---------------------------------- |
| Frontend               | React, Vite, Axios, React Markdown |
| Frontend Deployment    | Vercel                             |
| Backend                | FastAPI, Python                    |
| Backend Deployment     | Render                             |
| Database               | PostgreSQL                         |
| Web Scraping           | Playwright                         |
| AI Agent               | LangChain, OpenAI                  |
| Environment Management | Python venv, `.env`                |
| API Server             | Uvicorn                            |

---

## Database Design

The project stores reservation data at the following grain:

```txt
one row per reservation × stay_date
```

This is important because hotel revenue analysis should be based on `stay_date`, not only reservation creation date.

For example, a 3-night reservation creates 3 stay rows.

### Main Tables

```txt
reservations_hackathon
room_type_lookup
market_code_lookup
channel_code_lookup
rate_plan_lookup
macro_group_history
dataset_verification
```

### Main Fact Table

The `reservations_hackathon` table stores stay-level reservation data including:

* `reservation_stay_id`
* `reservation_id`
* `arrival_date`
* `departure_date`
* `stay_date`
* `reservation_status`
* `financial_status`
* `property_date`
* `guest_country`
* `space_type`
* `market_code`
* `channel_code`
* `rate_plan_code`
* `daily_room_revenue_before_tax`
* `daily_total_revenue_before_tax`
* `nights`
* `adr_room`
* `lead_time`
* `company_name`
* `travel_agent_name`

### Lookup Tables

The ETL loads the following lookup/reference tables:

| Table                  | Purpose                                      |
| ---------------------- | -------------------------------------------- |
| `room_type_lookup`     | Room type and room class metadata            |
| `market_code_lookup`   | Market segment metadata                      |
| `channel_code_lookup`  | Booking channel metadata                     |
| `rate_plan_lookup`     | Rate plan family and commissionable status   |
| `macro_group_history`  | Time-aware market macro group classification |
| `dataset_verification` | Verification values scraped from `/verify`   |

---

## Updated Dataset Support

The data portal was updated to include more reference and verification data. The ETL now supports the updated dataset structure.

The scraper now extracts:

* Reservation list pages
* Reservation detail pages
* Room type lookup
* Market code lookup
* Channel code lookup
* Rate plan lookup
* Macro group history
* Verification metadata from `/verify`

The database now stores:

* `financial_status`
* `property_date`
* `rate_plan_code`
* rate plan lookup data
* macro group history
* stay-date-aware macro group classification
* dataset revision
* posted OTB verification values
* reservation stay status checksum

---

## ETL Pipeline

The ETL pipeline performs three main stages.

### 1. Extract

The reservation website is JavaScript-rendered, so Playwright is used instead of basic HTTP requests.

The scraper:

* Opens the reference page
* Extracts room type lookup data
* Extracts market code lookup data
* Extracts channel code lookup data
* Extracts rate plan lookup data
* Extracts macro group history data
* Opens the verification page
* Extracts dataset revision and verification targets
* Opens the reservation list page
* Handles pagination
* Collects reservation detail links
* Opens each reservation detail page
* Extracts reservation-level fields
* Extracts one stay row per night

### 2. Transform

The scraped values are cleaned and converted into database-ready values:

* Dates are converted into date objects
* Date-times are converted into timezone-aware values
* Revenue values are converted into numeric values
* Boolean fields are converted into true/false values
* Blank or dash values are converted into null
* Reservation stay IDs are generated for each stay row
* Rate plan metadata is mapped into `rate_plan_lookup`
* Macro history validity dates are mapped into `macro_group_history`
* Verification values are mapped into `dataset_verification`

### 3. Load

The cleaned data is loaded into PostgreSQL.

The ETL is designed to be rerunnable. Existing rows are cleared before reloading so the database does not create duplicate data.

---

## Latest ETL Verification

Latest successful ETL verification:

| Check                          | Result |
| ------------------------------ | -----: |
| Total stay rows                |    531 |
| Total reservations             |    254 |
| Room type lookup rows          |      3 |
| Market code lookup rows        |     10 |
| Channel code lookup rows       |      4 |
| Rate plan lookup rows          |      8 |
| Macro group history rows       |     11 |
| Duplicate reservation stay IDs |      0 |
| Missing stay dates             |      0 |
| Missing total revenue          |      0 |

This confirms that the scraper, transformation logic, and database load are working correctly.

---

## Source Verification Metadata

The ETL also scrapes verification targets from the source portal `/verify` page.

Latest captured verification:

| Field                            |               Value |
| -------------------------------- | ------------------: |
| Dataset revision                 |      `2026.06.12.2` |
| Total reservations               |                 254 |
| Total stay rows                  |                 531 |
| Posted OTB room revenue          |          €93,273.00 |
| Posted OTB total revenue         |          €99,339.00 |
| Reservation stay status checksum | `7b9de2830c1b3da4…` |

The agent can answer verification questions such as:

```txt
Does my database match the source site?
What dataset revision is loaded?
Show posted OTB verification.
```

---

## Business Metrics

The backend exposes hotel revenue metrics through FastAPI and agent tools.

| Metric                   | Purpose                                         |
| ------------------------ | ----------------------------------------------- |
| Revenue by month         | Monthly on-the-books revenue, room nights, ADR  |
| Channel mix              | Booking channel contribution                    |
| OTA dependency           | OTA vs non-OTA revenue risk                     |
| Cancellations            | Cancelled business by stay month                |
| Room type ADR            | ADR and revenue by room type                    |
| Group business           | Group/block vs transient demand                 |
| Pickup last 7 days       | Recently created future business                |
| Market mix               | Market segment performance                      |
| Rate plan performance    | Revenue, ADR, and room nights by rate plan      |
| Financial status summary | Posted vs provisional revenue                   |
| Dataset verification     | Dataset revision and source verification values |

---

## API Endpoints

Backend API docs are available here:

```txt
https://hotel-revenue-manager-backend.onrender.com/docs
```

| Endpoint                      | Purpose                           |
| ----------------------------- | --------------------------------- |
| `/health`                     | Checks whether backend is running |
| `/verify`                     | Verifies ETL/database quality     |
| `/etl/run`                    | Runs the ETL pipeline again       |
| `/metrics/revenue-by-month`   | Monthly on-the-books revenue      |
| `/metrics/channel-mix`        | Booking channel contribution      |
| `/metrics/ota-dependency`     | OTA vs Non-OTA dependency         |
| `/metrics/cancellations`      | Cancelled business by stay month  |
| `/metrics/room-type-adr`      | ADR by room type                  |
| `/metrics/group-business`     | Group/block vs transient business |
| `/metrics/pickup-last-7-days` | Recent booking pickup             |
| `/metrics/market-mix`         | Market segment performance        |
| `/chat`                       | AI revenue manager chat endpoint  |

Depending on the current route setup, some newer metrics may be available through the chat agent tools rather than direct REST metric endpoints.

---

## Agent Tools

The agent is connected to backend tools including:

```txt
revenue_by_month_tool
channel_mix_tool
ota_dependency_tool
cancellations_by_month_tool
room_type_adr_tool
group_business_tool
pickup_last_7_days_tool
market_mix_tool
financial_status_summary_tool
rate_plan_performance_tool
dataset_verification_tool
refresh_database_tool
```

The agent selects the correct tool based on the user’s natural language question.

---

## Example Agent Questions

The frontend/API can be tested with questions such as:

```txt
What revenue is on the books by month?
Are we too dependent on OTA?
Which room type has the highest ADR?
Which rate plan performs best?
Show posted vs provisional revenue.
What changed in the last 7 days?
How much business was cancelled?
Which market segments are driving demand?
What is the market mix by macro group?
Does my database match the source site?
What dataset revision is loaded?
Show posted OTB verification.
Refresh the database.
```

---

## Example API Requests

### Chat Endpoint

```http
POST /chat
```

Request body:

```json
{
  "message": "Are we too dependent on OTA?"
}
```

Response format:

```json
{
  "question": "Are we too dependent on OTA?",
  "answer": "...",
  "tools_used": ["ota_dependency_tool"]
}
```

### Dataset Verification

```json
{
  "message": "Does my database match the source site?"
}
```

Example response summary:

```txt
The database matches the source verification targets for dataset revision 2026.06.12.2.

Total stay rows: 531
Total reservations: 254
Posted OTB total revenue: €99,339
Posted OTB room revenue: €93,273
```

### Dataset Revision

```json
{
  "message": "What dataset revision is loaded?"
}
```

Example response summary:

```txt
The loaded dataset revision is 2026.06.12.2.
```

### Posted OTB Verification

```json
{
  "message": "Show posted OTB verification."
}
```

Example response summary:

```txt
Posted OTB total revenue: €99,339
Posted OTB room revenue: €93,273
```

### Rate Plan Performance

```json
{
  "message": "Which rate plan performs best?"
}
```

### Posted vs Provisional Revenue

```json
{
  "message": "Show posted vs provisional revenue."
}
```

### Market Mix

```json
{
  "message": "What is the market mix by macro group?"
}
```

---

## Example Output

For the question:

```txt
Are we too dependent on OTA?
```

The agent can answer using real backend data:

```txt
OTA business represents a measurable share of total future reserved revenue.
Based on the OTA share, the hotel does not appear to be overly dependent on OTA demand.

Recommendation:
Continue strengthening direct booking channels while using OTAs selectively for demand generation during weaker periods.
```

For the question:

```txt
Show posted vs provisional revenue.
```

The agent can answer:

```txt
Posted revenue currently represents the majority of future reserved revenue.
Provisional revenue is much smaller and should be monitored because it may still change before final posting.
```

---

## Deployment

The application is deployed using:

* **Vercel** for the React frontend
* **Render** for the FastAPI backend
* **PostgreSQL** for persistent storage

### Deployed URLs

```txt
Frontend:
https://hotel-revenue-manager-agent.vercel.app/

Backend API Docs:
https://hotel-revenue-manager-backend.onrender.com/docs
```

### Deployment Notes

* The frontend communicates with the Render backend through the deployed API URL.
* CORS is enabled on the backend to allow frontend-backend communication.
* Environment variables are configured separately in Vercel and Render.
* The frontend has a simple basic auth layer for demo access.
* The backend API docs remain accessible for testing and inspection.
* The basic auth layer is intentionally simple and is not intended as production-grade authentication.

---

## Local Setup

### 1. Clone the project

```bash
git clone <repo-url>
cd hotel-revenue-manager-agent
```

### 2. Create Python virtual environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

Activate it on macOS/Linux:

```bash
source venv/bin/activate
```

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

Install Playwright browsers:

```bash
playwright install
```

### 4. Create `.env`

Create a `.env` file:

```env
DATABASE_URL=postgresql://user:password@host:5432/database
DATA_SITE_URL=https://otel-hackathon-data-site.vercel.app
OPENAI_API_KEY=your_openai_api_key_here
```

Do not commit real database credentials or API keys.

### 5. Set up PostgreSQL

You can use either:

* Local PostgreSQL through Docker
* A hosted PostgreSQL database such as Neon

If using Docker, start the database:

```bash
docker compose up -d
```

If using a hosted database, make sure `DATABASE_URL` points to the hosted database.

### 6. Apply schema

If the database is empty, apply the schema before running ETL.

Example:

```bash
psql "$DATABASE_URL" -f schema.sql
```

Alternatively, create the tables manually using `schema.sql`.

### 7. Run ETL

```bash
python -m app.etl
```

Expected successful output includes:

```txt
Transformed room types: 3
Transformed market codes: 10
Transformed channel codes: 4
Transformed rate plans: 8
Transformed macro group history rows: 11
Transformed reservation stay rows: 531
Loading dataset_verification...
ETL complete.
```

### 8. Start FastAPI backend

```bash
uvicorn app.main:app --reload
```

Backend runs locally at:

```txt
http://127.0.0.1:8000
```

FastAPI docs locally:

```txt
http://127.0.0.1:8000/docs
```

### 9. Start frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs locally at:

```txt
http://localhost:5173
```

---

## Project Structure

```txt
hotel-revenue-manager-agent/
├── app/
│   ├── agent.py
│   ├── db.py
│   ├── etl.py
│   ├── main.py
│   ├── metrics.py
│   ├── tools.py
│   └── skills/
│       ├── revenue_manager/
│       │   └── SKILL.md
│       ├── ota_analysis/
│       │   └── SKILL.md
│       └── pickup_cancellation/
│           └── SKILL.md
├── frontend/
│   └── src/
│       ├── App.jsx
│       ├── App.css
│       └── api.js
├── docker-compose.yml
├── schema.sql
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## Important Business Logic

The project follows these business rules:

* Hotel performance is measured using `stay_date`
* Cancelled reservations are excluded from on-the-books metrics
* Cancellations are analyzed separately
* Reservation count uses `COUNT(DISTINCT reservation_id)`
* Room nights use `SUM(number_of_spaces)`
* Room revenue uses `SUM(daily_room_revenue_before_tax)`
* Total revenue uses `SUM(daily_total_revenue_before_tax)`
* ADR uses room revenue divided by room nights where applicable
* Room type ADR can use the `adr_room` field averaged by room type
* OTA dependency is identified using OTA market codes and OTA source names
* Group business is identified using block bookings and group-style market codes
* Macro group classification uses `macro_group_history` by stay date where available
* Static market lookup is used as a fallback when no historical macro group match exists
* Posted vs provisional revenue uses `financial_status`
* Dataset verification uses the latest scraped `/verify` metadata

---

## Current Status

Completed:

* PostgreSQL schema
* Playwright ETL scraper
* Reservation pagination scraping
* Reservation detail scraping
* Edge-case reservation ID support
* Data transformation and load
* Room type lookup loading
* Market code lookup loading
* Channel code lookup loading
* Rate plan lookup loading
* Macro group history loading
* Financial status support
* Property date support
* Dataset verification scraping
* FastAPI metrics API
* LangChain tool layer
* AI revenue manager agent
* `/chat` endpoint
* React frontend
* Simple frontend basic auth layer
* Frontend deployment on Vercel
* Backend deployment on Render
* Verification tool routing
* Rate plan performance tool
* Posted vs provisional revenue tool
* Stay-date-aware market mix logic

Remaining:

* Screenshots
* Optional production-grade authentication
* Optional automated daily ETL refresh
* Optional dashboard charts

---

## Future Improvements

* Add production-grade authentication
* Add charts for monthly revenue and market mix
* Add conversation history
* Add downloadable revenue summary reports
* Add daily automated ETL refresh
* Add more advanced forecasting and pricing recommendations
* Add same-time-last-year comparison as a dedicated metric
* Add full checksum extraction from raw JSON if exposed by the verification page
* Add dashboard cards for dataset revision and ETL health
