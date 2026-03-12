IceGuard AI: Geospatial Iceberg IntelligenceAutomated SAR Detection & LLM-Driven Maritime Risk AssessmentIceGuard AI is a geospatial intelligence platform designed for the North Atlantic maritime sector. It bridges the gap between raw Sentinel-1 SAR data and human-readable risk intelligence. By combining classical geospatial processing with Retrieval-Augmented Generation (RAG), IceGuard AI detects hazards and generates IMO-standardized safety reports for offshore operators.🏗 System ArchitectureIceGuard AI is built on a Modular Monolith architecture, designed to evolve from a prototype into a distributed event-driven system.Architecture OverviewIngestion Layer: Connects to the Sentinel Hub API to fetch and terrain-correct SAR GRD scenes.Detection Engine: A decoupled module that runs CFAR (Constant False Alarm Rate) or ML-based detection, outputting standardized GeoJSON iceberg centroids.Knowledge Base (Pinecone): Stores vectorized maritime SOPs, historical iceberg charts, and incident reports to ground the LLM's logic.Reporting Chain (LangChain): An intelligent agent that merges live detections with historical context from the Vector DB to synthesize safety advisories.Analytics Dashboard: A Streamlit interface for map-based exploration and report validation.💻 Tech StackCategoryToolsLLM & RAGOpenAI GPT-4o, LangChain (Orchestration)Vector MemoryPinecone (High-performance similarity search for geospatial context)GeospatialSentinelHub, GeoPandas, Shapely, FionaData ScienceNumPy, Pandas, PyArrow (Parquet support)FrontendStreamlit (Interactive Operational Dashboard)🚀 Getting Started1. PrerequisitesPython 3.9+Sentinel Hub Account (for SAR data)OpenAI API Key & Pinecone API Key2. InstallationBash# Clone the repository
git clone https://github.com/your-username/iceguard-ai.git
cd iceguard-ai

# Initialize virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
3. Environment ConfigurationCreate a .env file in the root directory:BashOPENAI_API_KEY=your_key_here
PINECONE_API_KEY=your_key_here
PINECONE_ENV=us-east-1
SH_CLIENT_ID=your_id
SH_CLIENT_SECRET=your_secret
4. Launching the PlatformBash# Start the Integrated Dashboard
streamlit run frontend/app.py
🧪 Testing & ReliabilityWe follow the Testing Pyramid to ensure maritime-grade reliability:Unit Tests: Focused on preprocessing.py and geospatial math using pytest.Integration Tests: Validates the JSON contract between the Detection Engine and the Reporting Chain.E2E Validation: Visual regression checks on the Streamlit map layers and LLM output auditing.🗺 Roadmap[ ] Multi-Sensor Fusion: Integrating Sentinel-2 (Optical) to cross-verify SAR detections.[ ] Near-Real-Time (NRT) Alerts: Webhook integration for SMS/Email alerts when an iceberg enters a specified safety buffer.[ ] Edge Deployment: Researching lightweight detection models for vessel-side deployment.