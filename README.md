## IceGuard AI – Geospatial Iceberg Detection & Maritime Risk Intelligence

IceGuard AI is a geospatial intelligence platform for **automatic iceberg detection and maritime safety reporting**. It is designed to ingest Sentinel‑1 SAR data, detect icebergs with a detection engine, and use an LLM to generate **actionable risk assessments** for maritime stakeholders (shipping, offshore operations, search and rescue).

The project structure and architecture below are intentionally modular to support a clear **Thinking → Prototyping → Production** evolution, and to align with C‑CORE’s strengths in Remote Sensing, AI, and operational systems.

---

## Vision

- **Trusted iceberg intelligence**: Turn raw Sentinel‑1 SAR acquisitions into verified iceberg detections with associated confidence and metadata.
- **Operational maritime safety**: Deliver concise, LLM‑generated reports highlighting navigational hazards, risk levels, and recommended courses of action.
- **Modular, research‑friendly stack**: Make it easy to iterate on ingestion strategies, detection models, and reporting prompts independently.


I built this as a Modular Monolith to ensure rapid iteration and easy debugging during the prototype phase. 
However, I will designe the data contracts (GeoJSON/Parquet) so that we could easily migrate the Detection Engine to a Microservice or an Event-Driven pipeline once we need to scale for real-time North Atlantic monitoring.



Core questions IceGuard AI aims to answer:

- Where are icebergs within the latest Sentinel‑1 SAR scenes?
- How confident are we in each detection, and how does it evolve over time?
- What is the **implication for vessels, offshore infrastructure, and shipping lanes**?
- How can we translate detections and geospatial context into **clear, human‑readable guidance**?

---

## High‑Level Architecture

At a high level, IceGuard AI is organized into four main components:

- **`data_ingestion/`** – Acquire, cache, and pre‑process Sentinel‑1 SAR data.
- **`detection_engine/`** – Run iceberg detection pipelines on pre‑processed SAR imagery.
- **`llm_reporting/`** – Turn detections and geospatial context into LLM‑generated maritime safety reports.
- **`frontend/`** – A Streamlit‑based UI for interactive exploration and reporting.

These components are loosely coupled via **clear data contracts** (e.g., well‑defined JSON/GeoJSON artifacts and intermediate parquet/NetCDF products) so that improvements in one module do not require invasive changes elsewhere.

---

## Repository Layout

Intended top‑level layout:

- **`.env`**
  - Central configuration (API keys, index names, provider settings, etc.).

- **`requirements.txt`**
  -  Python dependencies for reproducibility, including `sentinelhub`, `shapely`, `geopandas`, `langchain`, and `streamlit`.


- **`data_ingestion/`**
  - `__init__.py` – Package marker and shared types/interfaces.
  - `sentinel_client.py` – Thin wrapper around the `sentinelhub` Python package for querying and downloading Sentinel‑1 SAR scenes.
  - `preprocessing.py` – Radiometric calibration, speckle filtering, incidence angle normalization, land/sea masking, and tiling logic.
  - (Future) `catalog.py` – Scene catalog abstraction (search by AOI, time range, orbit, polarization, etc.) plus local cache management.

- **`detection_engine/`**
  - `__init__.py` – Package marker and core interfaces for detectors.
  - (Future) `models/` – Model definitions (e.g., classical CFAR‑based detectors, CNN/UNet/Transformer models, or hybrid approaches).
  - (Future) `pipelines.py` – End‑to‑end detection pipelines (load tiles → run detector → post‑process → generate iceberg objects).
  - (Future) `postprocessing.py` – Clustering, false positive reduction, and conversion to vector geometries (e.g., iceberg polygons or centroids).

- **`llm_reporting/`**
  - `__init__.py` – Package marker and interfaces for report generation.
  - (Future) `schema.py` – Pydantic models describing iceberg detections, region summaries, and report templates.
  - (Future) `prompts.py` – Prompt templates to condition the LLM on maritime safety context, IMO guidelines, and client‑specific style.
  - (Future) `reporting_chain.py` – LangChain‑based chains or agents that:
    - Ingest detections, routes, and contextual layers.
    - Retrieve historical observations and relevant domain knowledge.
    - Generate structured, auditable safety reports.

- **`frontend/`**
  - `app.py` – Streamlit entry point for the IceGuard AI UI.
  - (Future) `views/` – Page‑level components (e.g., “Operational Overview”, “Scene Explorer”, “Report Builder”).
  - (Future) `components/` – Reusable widgets (map viewers, time sliders, detection summary panels, etc.).
  - (Future) `state.py` – Simple app‑level state handling (e.g., selected AOI, time range, vessel route).

  

---

## Data Flow (End‑to‑End)

1. **Tasking & AOI Definition**
   - Operator defines Areas of Interest (AOIs), time windows, and operational constraints (e.g., vessel route, platform location).
   - AOIs and constraints are stored in configuration or provided via the Streamlit UI.

2. **SAR Data Ingestion (`data_ingestion/`)**
   - Use `sentinelhub` to query Sentinel‑1 SAR scenes matching AOI/time filters.
   - Download or stream scenes into a local cache or object store.
   - Apply initial pre‑processing:
     - Calibration and terrain correction, speckle filtering.
     - Land/sea masking and incidence‑angle normalization.
     - Tiling into analysis‑ready patches.

3. **Iceberg Detection (`detection_engine/`)**
   - For each pre‑processed tile:
     - Run the configured detector (CFAR, ML model, or hybrid).
     - Generate iceberg candidates with location, size, backscatter, and confidence scores.
   - Aggregate tile‑level detections into scene‑level and AOI‑level products.
   - Export detections as **GeoJSON** or similar geospatial formats to feed downstream systems.

4. **Risk Contextualization & LLM Reporting (`llm_reporting/`)**
   - Enrich detections with:
     - Shipping lanes, vessel tracks, and dynamic AIS information.
     - Offshore infrastructure, exclusion zones, and environmental data (sea ice, currents).
   - Use LangChain‑based chains to:
     - Ingest detection+context data.
     - Retrieve relevant domain knowledge (e.g., guidelines, SOPs, past incident reports).
     - Generate structured maritime safety reports with:
       - Clear statement of risk level.
       - Spatial/temporal summaries of ice conditions.
       - Recommended actions and caveats.

5. **Frontend Visualization (`frontend/`)**
   - Streamlit app provides:
     - Interactive map of iceberg detections and AOIs.
     - Time‑series views of risk evolution.
     - A panel for LLM‑generated reports, with export (PDF, HTML, text) options.
   - Operators can review, edit, and approve LLM outputs before dissemination.

---

## Technology Stack

- **Remote Sensing & Geospatial**
  - `sentinelhub` – Sentinel Hub Python client for Sentinel‑1 SAR acquisition.
  - `shapely`, `geopandas` – Geometry operations, spatial joins, and vectorized geospatial analysis.
  - `numpy`, `pandas` – Numerical and tabular processing.

- **AI & LLM Reporting**
  - `langchain` – Orchestration layer for LLM calls, retrieval, and chains.
  - (Future) Provider‑specific LLM SDKs (e.g., OpenAI, Anthropic, Azure, etc.).

- **Frontend & Delivery**
  - `streamlit` – Streamlit-based UI for operators and analysts.

- **Utilities**
  - `python-dotenv`, `requests`, and related helpers for configuration and HTTP integrations.

---

## Getting Started 

1. **Environment setup**
   - Create and activate a Python virtual environment (e.g., `python -m venv .venv`).
   - Install dependencies:

```bash
pip install -r requirements.txt
```

2. **Configuration**
   - Populate `config.yaml` or a `.env` file with:
     - Sentinel Hub credentials.
     - LLM provider API keys.
     - Storage locations / buckets.
   - Avoid committing real secrets to version control; prefer environment variables or a secrets manager.

3. **Run the Streamlit frontend**

```bash
streamlit run frontend/app.py
```

4. **Next steps**
   - Implement the Sentinel‑1 ingestion pipeline in `data_ingestion/`.
   - Prototype a baseline detection pipeline in `detection_engine/` (e.g., CFAR + rule‑based post‑processing).
   - Design reporting schemas and prompts in `llm_reporting/` and wire them into the Streamlit app.

---

## Roadmap Ideas

- Integrate additional sensors (e.g., Sentinel‑2, commercial SAR) for multi‑sensor confirmation.
- Add continuous monitoring and alerting (email/SMS/webhooks) for high‑risk detections.
- Introduce model evaluation dashboards (precision/recall vs. validated ground truth).
- Support batch and near‑real‑time modes to match operational constraints.