# Hotel Revenue Manager Agent

An AI-powered hotel revenue management assistant that helps a General Manager ask business questions about on-the-books revenue, ADR, OTA dependency, cancellations, pickup, room types, and market mix.

The system scrapes reservation data from a JavaScript-rendered hotel data portal, loads the data into Postgres, exposes verified business metrics through FastAPI, and connects those metrics to an AI agent that answers questions in plain business language.

---

## Project Overview

Hotel revenue managers need to understand business performance across several dimensions:

* Monthly on-the-books revenue
* Room nights and ADR
* OTA dependency
* Channel mix
* Market segment mix
* Room type performance
* Cancellations
* Recent booking pickup

Instead of manually checking multiple reports, this project allows a user to ask natural language questions such as:

* What revenue is on the books by month?
* Are we too dependent on OTA?
* Which room type has the highest ADR?
* What changed in the last 7 days?
* Which market segments are driving demand?

The AI agent uses trusted backend tools and database metrics rather than inventing answers.

---

## Key Features

* Playwright-based web scraping for JavaScript-rendered reservation data
* ETL pipeline to extract, clean, transform, and load reservation data
* Postgres database running through Docker
* FastAPI backend with health, verification, metrics, and chat endpoints
* LangChain tool layer connected to verified business metrics
* Deep Agent-style AI revenue manager assistant
* React frontend for asking hotel business questions
* Markdown-rendered AI responses
* CORS-enabled frontend-backend communication

---

## Architecture

```txt
Hotel Data Website
    ↓
Playwright Scraper
    ↓
ETL Transformation
    ↓
Postgres Database
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
| Backend                | FastAPI, Python                    |
| Database               | PostgreSQL                         |
| Database Runtime       | Docker                             |
| Web Scraping           | Playwright                         |
| AI Agent               | Deep Agents, LangChain, OpenAI     |
| Environment Management | Python venv, `.env`                |

---

## Database Design

The project uses four main tables:

```txt
reservations_hackathon
room_type_lookup
market_code_lookup
channel_code_lookup
```

The main reservation table is stored at the grain:

```txt
one row per reservation × stay_date
```

This is important because hotel revenue analysis should use `stay_date`, not only reservation creation date.

For example, a 3-night reservation creates 3 stay rows.

---

## ETL Pipeline

The ETL pipeline performs three steps:

### 1. Extract

The reservation website is JavaScript-rendered, so Playwright is used instead of basic HTTP requests.

The scraper:

* Opens the reservation list page
* Handles pagination
* Collects reservation detail links
* Opens each reservation detail page
* Extracts reservation fields
* Extracts one stay row per night
* Extracts room type, market code, and channel code lookup tables

### 2. Transform

The scraped website values are cleaned and converted into database-ready values:

* Dates are converted into date objects
* Revenue values are converted into numeric values
* Boolean fields are converted into true/false values
* Blank or dash values are converted into null
* Reservation stay IDs are generated for each stay row

### 3. Load

The cleaned data is loaded into Postgres.

The ETL is designed to be rerunnable. Existing rows are cleared before reloading so the database does not create duplicate data.

---

## ETL Verification

Latest successful verification:

| Check                          | Result |
| ------------------------------ | -----: |
| Total stay rows                |    534 |
| Total reservations             |    250 |
| Room type lookup rows          |      3 |
| Market code lookup rows        |     10 |
| Channel code lookup rows       |      4 |
| Duplicate reservation stay IDs |      0 |
| Missing stay dates             |      0 |
| Missing total revenue          |      0 |

This confirms that the scraper, transformation logic, and database load are working correctly.

---

## Business Metrics

The backend exposes hotel revenue metrics through FastAPI.

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

---

## Example Agent Questions

The frontend includes suggested questions such as:

```txt
What revenue is on the books by month?
Are we too dependent on OTA?
Which room type has the highest ADR?
What changed in the last 7 days?
How much business was cancelled?
Which market segments are driving demand?
```

---

## Example Output

For the question:

```txt
Are we too dependent on OTA?
```

The agent can answer using real backend data:

```txt
OTA business represents 18.43% of total revenue, while Non-OTA business represents 81.57%.
This suggests the hotel is not overly dependent on OTA demand.

Recommendation:
Continue strengthening direct booking channels while using OTAs selectively for demand generation during weaker periods.
```

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

Activate it:

```bash
venv\Scripts\activate
```

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 4. Create `.env`

Create a `.env` file:

```env
DATABASE_URL=postgresql://hackathon:hackathon@localhost:5432/hotel_hackathon
DATA_SITE_URL=https://otel-hackathon-data-site.vercel.app
OPENAI_API_KEY=your_openai_api_key_here
```

### 5. Start Postgres using Docker

```bash
docker compose up
```

### 6. Run ETL

In another terminal:

```bash
python -m app.etl
```

### 7. Start FastAPI backend

```bash
uvicorn app.main:app --reload
```

Backend runs at:

```txt
http://127.0.0.1:8000
```

FastAPI docs:

```txt
http://127.0.0.1:8000/docs
```

### 8. Start frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at:

```txt
http://localhost:5173
```

---

## API Usage

### Chat endpoint

```http
POST /chat
```

Request body:

```json
{
  "message": "Are we too dependent on OTA?"
}
```

Response:

```json
{
  "question": "Are we too dependent on OTA?",
  "answer": "..."
}
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

The project follows these rules:

* Hotel performance is measured using `stay_date`
* Cancelled reservations are excluded from on-the-books metrics
* Cancellations are analyzed separately
* Reservation count uses `COUNT(DISTINCT reservation_id)`
* Room nights use `SUM(number_of_spaces)`
* Room revenue uses `SUM(daily_room_revenue_before_tax)`
* Total revenue uses `SUM(daily_total_revenue_before_tax)`
* Room type ADR uses the `adr_room` field averaged by room type

---

## Current Status

Completed:

* Docker Postgres setup
* Database schema
* Playwright ETL scraper
* Data transformation and load
* ETL verification
* FastAPI metrics API
* LangChain tool layer
* AI revenue manager agent
* `/chat` endpoint
* React frontend

Remaining:

* Deployment
* Screenshots
* Optional authentication
* Final polish

---

## Future Improvements

* Add authentication for deployed version
* Add charts for monthly revenue and market mix
* Add conversation history
* Add downloadable revenue summary reports
* Add more advanced forecasting and pricing recommendations
* Add daily automated ETL refresh
