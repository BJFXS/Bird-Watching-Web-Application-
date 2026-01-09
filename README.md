# Bird-Watching Web Application

A full-stack bird-watching web application inspired by **eBird**, built with **Vue.js** and interactive map visualizations. 
The app enables users to record bird sightings, explore bird activity geographically, and analyze personal and regional bird-watching statistics.

---

## Project Overview

This project focuses on building a **data-driven, map-centric web application** that supports:

- Recording bird sightings with geolocation
- Visualizing bird density on interactive maps
- Exploring regional bird statistics and trends
- Tracking personal bird-watching history

The system emphasizes **clean UI design**, **client–server interaction**, and **practical data visualization** using real-world-style datasets.

---

## Features

###  Interactive Map (Index Page)
- Heatmap visualization of bird sightings
- Species-based filtering
- Rectangle selection for regional analysis
- Quick navigation to checklist and statistics pages

###  Checklist Submission
- Log bird sightings with:
- Species selection
- Counts per species
- Geolocation and observation duration
- Incremental input with live timers
- Persistent storage via backend APIs

###  Regional Statistics
- Species summaries within a selected region
- Time-series visualizations of sightings
- Top contributor rankings
- Interactive charts for deeper exploration

###  User Statistics
- Personal bird-watching history
- First-seen and most-recently-seen species
- Searchable species lists
- Trend analysis over time

---

## Tech Stack

### Frontend
- **Vue.js (Vue 3)**
- **JavaScript**
- **Axios** (API communication)
- **Leaflet.js** (map rendering & drawing)
- **Leaflet.heat** (heatmap visualization)
- **Chart.js** (statistics & trends)

### Backend
- RESTful API endpoints
- Relational database for:
- Species
- Checklists
- Sightings
- User statistics

### Data
- Preloaded synthetic bird-watching datasets
- Structured to resemble real-world eBird data

---

##  Application Structure

### Frontend (Vue.js)
| File | Description |
|-----|------------|
| `index.js` | Interactive map view with heatmap visualization and region selection |
| `checklist.js` | Checklist creation, species input, timers, and submission logic |
| `location.js` | Regional statistics view with species breakdowns and contributors |
| `statistics.js` | User-level statistics and trend visualizations |
| `axios.js` | Centralized API request configuration |

### Backend
| File | Description |
|-----|------------|
| `models.py` | Relational database schema for species, checklists, and sightings |
| `controllers.py` | REST API endpoints and request handling |
| `tasks.py` | Data initialization and background tasks |
| `common.py` | Shared backend utilities and helpers |

---


##  Getting Started

### Prerequisites

Ensure the following tools are installed:

- **Node.js** (v16 or later)
- **npm** or **yarn**
- **Python 3.8+**
- **SQLite or PostgreSQL**
- Internet access (for map tiles and APIs)

---

### Installation

#### 1. Clone the Repository

```bash
git clone https://github.com/your-username/bird-watching-app.git
cd bird-watching-app
```

#### 2. Frontend Setup

Install Dependencies
```bash
npm install
```

Run Development Server
```bash
npm run serve
```

Once started, the frontend will be available at:
```bash
http://localhost:8080
```


#### 3. Backend Setup

Create Virtual Environment (Recommended)
```bash
python -m venv venv
source venv/bin/activate   # macOS / Linux
venv\Scripts\activate      # Windows
```

Install Backend Dependencies
```bash
pip install -r requirements.txt
```

Start Backend Server
```bash
python server.py
```

The backend API will run at:
```bash
http://localhost:8000
```



#### 4. Database Initialization

The database initializes automatically on first run.

To manually load sample data:
```bash
python tasks.py
```
