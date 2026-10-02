# AI-Powered Side-Scan Sonar Marine Debris Detection, Verification, Geolocation and Cleanup Prioritization Platform

**Status**: Phase 20 - Final Integration & SIH Demo (COMPLETE) ✓

A complete, production-ready platform for detecting, analyzing, and prioritizing marine debris using AI-powered side-scan sonar imagery. Built with YOLOv8 deep learning, acoustic shadow analysis, and geospatial intelligence.

This project runs **entirely locally on the user's laptop** (localhost frontend → localhost FastAPI → local SQLite → local YOLO model). No cloud deployment, external LLM, or API key is required for the SIH demo.

## 🎯 Project Overview

Marine debris poses significant environmental and safety hazards. This platform automates debris detection in sonar imagery, applies computer vision heuristics for verification, estimates geographic locations, and prioritizes cleanup operations using a transparent scoring system.

### Core Problem

- Manual sonar data review is time-consuming
- False positives require human verification
- Debris prioritization is subjective
- Limited scalability for large survey areas

### Our Solution

- **YOLOv8-powered detection** trained on custom debris classes
- **Acoustic shadow analysis** for plausibility verification
- **False-positive filtering** using confidence + heuristics
- **GPS geolocation** from sonar metadata
- **Transparent priority scoring** for cleanup planning
- **LLM assistant** for natural language queries
- **Professional dashboard** for visualization and reporting

## 📋 Features

### Data Processing Pipeline

- ✅ Multi-format ingestion (JPG, PNG, TIFF, XTF, JSF)
- ✅ Batch processing support
- ✅ Data validation with detailed reporting
- ✅ Intelligent preprocessing (denoising, normalization, CLAHE)
- ✅ Unique processing IDs for audit trails

### Phase 4: Sonar Data Validation

Validation runs after Phase 3 ingestion and before preprocessing. Every run is retained in the `validation_runs` table.

- `VALID`: all assessable checks pass; ready for preprocessing
- `WARNING`: usable with missing or non-critical information; ready for preprocessing
- `REJECTED`: unusable, corrupt, malformed, or unsupported; blocked from preprocessing
- Image checks measure readability, dimensions, channels, pixel validity, blankness, intensity statistics, near-zero pixels, saturation, and an evidence-derived quality score.
- XTF validation uses the installed `pyxtf` parser where assessable. JSF files receive basic file checks and clearly report that detailed validation is unavailable when no real parser is configured.
- Metadata validation checks timestamps, dimensions, numeric values, and GPS ranges. Missing GPS is reported as `UNAVAILABLE` and produces a warning; coordinates are never fabricated.
- Batch validation processes each ingested file independently and reports valid, warning, and rejected totals.
- Demo files use the same validation pipeline as real files.
- `ready_for_preprocessing` is `true` for `VALID` and `WARNING`, and `false` for `REJECTED`.

### Phase 5: Sonar Image Preprocessing

Validated `VALID` and `WARNING` images can be processed; `REJECTED` files are blocked. Originals in `data/raw` are never modified. Processed PNGs are written to `data/processed` and run metadata is written to `data/preprocessing`.

- Supports JPG, JPEG, PNG, TIFF, and TIF.
- Normalizes grayscale, RGB, and alpha images to a grayscale intensity image without blindly converting sonar data to RGB.
- Applies configurable Gaussian, median, or bilateral denoising, CLAHE local contrast enhancement, and min-max or percentile intensity normalization.
- Resizes with aspect-ratio preservation and optional padding. The default target is 640 x 640.
- Records original/processed dimensions, resize ratio, padding, before/after intensity statistics, and processing time in append-only `preprocessing_runs` records.
- Demo images use the same real pipeline and processed images are available through the API for before/after views.

Configuration variables: `PREPROCESS_ENABLED`, `DENOISE_METHOD`, `DENOISE_KERNEL_SIZE`, `DENOISE_SIGMA`, `CLAHE_CLIP_LIMIT`, `CLAHE_TILE_GRID_SIZE`, `NORMALIZATION_METHOD`, `PREPROCESS_TARGET_SIZE`, and `PRESERVE_ASPECT_RATIO`.

Preprocessing endpoints:

- `POST /api/preprocessing/files/{file_id}`
- `GET /api/preprocessing/files/{file_id}`
- `GET /api/preprocessing/{preprocessing_id}`
- `GET /api/preprocessing/{preprocessing_id}/image`
- `POST /api/preprocessing/batch`

Run preprocessing tests with `pytest tests/unit/test_preprocessing.py -q`.

### AI Detection

- ✅ YOLOv8 custom model (4 debris classes: net, pipe, wreck, debris)
- ✅ CUDA GPU acceleration (auto-fallback to CPU)
- ✅ Configurable confidence thresholds
- ✅ Bounding box extraction
- ✅ Frame-level detection metadata

### Verification & Analysis

- ✅ Acoustic shadow analysis heuristic
- ✅ False-positive filtering
- ✅ Confidence scoring
- ✅ Shape and geometry analysis
- ✅ Decision labels: CONFIRMED, POSSIBLE, REJECTED

### Geolocation

- ✅ GPS metadata extraction from sonar files
- ✅ Manual coordinate input (clearly labeled)
- ✅ Unavailability handling (shows reason)
- ✅ Geographic filtering on dashboard

### Database & Reporting

- ✅ SQLite backend (PostgreSQL-ready schema)
- ✅ Complete detection history
- ✅ CSV export
- ✅ JSON export
- ✅ Filtered and full reports

### Dashboard & Visualization

- ✅ Professional React + Tailwind UI
- ✅ Real-time statistics
- ✅ Detection results viewer
- ✅ Confidence distribution charts
- ✅ Map visualization (Leaflet)
- ✅ Priority-based filtering

### AI Assistant

- ✅ LLM integration (OpenAI + Ollama support)
- ✅ Natural language queries
- ✅ Survey summarization
- ✅ Cleanup recommendations
- ✅ Graceful degradation if LLM unavailable

### Model Management

- ✅ Model versioning
- ✅ Training pipeline
- ✅ Evaluation metrics
- ✅ ONNX export support
- ✅ Edge deployment ready

## 🏗️ Architecture

### Backend Stack

```
FastAPI (REST API)
    ↓
Pydantic (Validation)
    ↓
Service Layer:
  ├── Data Ingestion
  ├── Validation
  ├── Preprocessing
  ├── YOLOv8 Detection
  ├── Shadow Analysis
  ├── False-Positive Filtering
  ├── Geolocation
  ├── Database Management
  ├── Report Generation
  ├── Priority Scoring
  └── LLM Integration
    ↓
SQLite/PostgreSQL
```

### Frontend Stack

```
React + Vite
    ↓
Tailwind CSS
    ↓
Leaflet Maps
    ↓
FastAPI Backend
```

### ML Pipeline

```
Raw Sonar Image
    ↓
Validation
    ↓
Preprocessing
    ↓
YOLOv8 Model
    ↓
Detections + Confidence
    ↓
Shadow Analysis
    ↓
False-Positive Filter
    ↓
Geolocation
    ↓
Database Storage
    ↓
Priority Calculation
    ↓
Dashboard Display
```

## 📦 Project Structure

```
sonar-debris-ai/
│
├── backend/                          # Python FastAPI backend
│   ├── main.py                       # Application entry point
│   ├── api/                          # REST API endpoints
│   ├── models/                       # Pydantic data models
│   ├── schemas/                      # Request/response schemas
│   ├── services/
│   │   ├── sonar/                   # Sonar file parsing
│   │   ├── validation/              # Data validation
│   │   ├── preprocessing/           # Image preprocessing
│   │   ├── detection/               # YOLOv8 inference
│   │   ├── shadow/                  # Acoustic shadow analysis
│   │   ├── filtering/               # False-positive filtering
│   │   ├── geolocation/             # GPS/coordinate handling
│   │   ├── database/                # SQLAlchemy ORM
│   │   ├── reports/                 # CSV/JSON generation
│   │   ├── priority/                # Cleanup prioritization
│   │   └── llm/                     # LLM provider abstraction
│   ├── database/                     # Database models
│   └── utils/                        # Helper functions
│
├── frontend/                         # React + Vite frontend
│   ├── src/
│   │   ├── components/              # Reusable UI components
│   │   ├── pages/                   # Page components
│   │   ├── services/                # API client
│   │   ├── hooks/                   # React hooks
│   │   └── maps/                    # Map components
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
│
├── training/                         # YOLOv8 training pipeline
│   ├── dataset/                     # Dataset structure
│   ├── scripts/
│   │   ├── prepare_dataset.py       # Data preparation
│   │   ├── validate_dataset.py      # Dataset validation
│   │   ├── train_yolov8.py          # Training script
│   │   ├── evaluate_model.py        # Model evaluation
│   │   └── export_model.py          # ONNX/TorchScript export
│   ├── dataset.yaml                 # YOLOv8 config
│   └── README.md
│
├── data/
│   ├── demo/                        # Demo assets (clearly marked)
│   ├── raw/                         # Raw sonar files (ignored by Git)
│   ├── processed/                   # Processed frames (ignored by Git)
│   └── exports/                     # Generated reports (ignored by Git)
│
├── models/
│   └── README.md                    # Model storage guide
│
├── tests/
│   ├── unit/                        # Unit tests
│   └── integration/                 # Integration tests
│
├── scripts/
│   └── check_repo.py               # Pre-commit safety checker
│
├── docs/
│   ├── architecture.md             # Architecture overview
│   ├── ai_pipeline.md              # Detailed AI pipeline
│   ├── dataset.md                  # Dataset guide
│   ├── geolocation.md              # Geolocation handling
│   ├── llm.md                      # LLM integration
│   ├── api.md                      # API reference
│   ├── deployment.md               # Deployment guide
│   └── hackathon_demo.md           # Demo instructions
│
├── .env.example                     # Environment template
├── .gitignore                       # Git ignore rules
├── README.md                        # This file
├── LICENSE                          # Project license
├── requirements.txt                 # Python dependencies
├── docker-compose.yml              # Docker configuration
└── package.json                     # (root-level if using lerna/monorepo)
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- Git
- CUDA 11.8+ (optional, for GPU acceleration)

### 1. Clone Repository

```bash
git clone <your-repository-url>
cd sonar-debris-ai
```

### 2. Environment Setup

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your configuration
# REQUIRED:
#   - DATABASE_URL (defaults to SQLite)
#   - API_RELOAD=true (for development)
#   - LLM_PROVIDER=disabled (or openai/ollama)
#
# If using OpenAI:
#   - OPENAI_API_KEY=your_key
#
# If using Ollama (local):
#   - OLLAMA_BASE_URL=http://localhost:11434
#   - OLLAMA_MODEL=llama2
#
# If training:
#   - TRAINING_DEVICE=cuda (or cpu)
```

### 3. Backend Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Frontend Setup

```bash
cd frontend
npm install
npm run dev  # Starts dev server at http://localhost:5173
```

### 5. Start Backend

```bash
# From project root
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### 6. Access Application

- **Frontend**: http://localhost:5173
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 📊 Pipeline Explanation

### Data Ingestion

Accepts JPG, PNG, TIFF, XTF, and JSF files. Each upload receives a unique processing ID and is validated before entering the pipeline.

### Validation

Checks file integrity, dimensions, format, and metadata. Results stored with status (VALID, WARNING, REJECTED) and detailed error messages.

### Preprocessing

- **Denoising**: Reduces noise artifacts
- **Normalization**: Standardizes intensity ranges
- **CLAHE**: Contrast-Limited Adaptive Histogram Equalization
- **Resizing**: Standardizes to model input dimensions

All preprocessing is configurable and original images are preserved.

### YOLOv8 Detection

Custom-trained model detects 4 debris classes:

- **net**: Fishing nets
- **pipe**: Pipe fragments
- **wreck**: Shipwreck debris
- **debris**: Unclassified debris

Outputs: class, bounding box, confidence score, frame ID.

### Acoustic Shadow Analysis

For each detection, analyzes the shadow region beneath the object:

1. Crops detection area and shadow region
2. Applies adaptive thresholding
3. Performs morphological processing
4. Extracts contours and geometry
5. Calculates plausibility score

**Important**: Labeled as COMPUTER VISION HEURISTIC, not absolute physical proof.

### False-Positive Filtering

Combines three scores with configurable weights:

- **Model Confidence** (default 0.50): Direct from YOLOv8
- **Shadow Score** (default 0.30): Acoustic shadow plausibility
- **Shape Score** (default 0.20): Geometric properties

Decision: CONFIRMED, POSSIBLE, or REJECTED with explanation.

### Geolocation

Extracts GPS metadata from sonar files when available. Manual input explicitly labeled as "MANUALLY ASSIGNED LOCATION". Shows unavailability reason if metadata missing.

### Database Storage

SQLite stores:

- Detections with all scores
- Geolocation data
- Confidence distributions
- Processing metadata
- Model versions
- Training runs

PostgreSQL-ready schema for production deployment.

### Cleanup Priority

Transparent scoring system based on:

- Object type (debris > pipe > net > wreck)
- Confidence score
- Estimated size
- Shadow plausibility
- Optional shipping-lane proximity data

Outputs: CRITICAL, HIGH, MEDIUM, LOW with clear methodology documentation.

## 🎓 YOLOv8 Model Training

### Dataset Preparation

Place training images in `data/raw/`. Use annotation tools like Roboflow or CVAT.

```bash
cd training
python scripts/prepare_dataset.py
python scripts/validate_dataset.py
```

### Training

```bash
python scripts/train_yolov8.py \
  --epochs 100 \
  --batch-size 16 \
  --img-size 640 \
  --device cuda \
  --lr 0.001
```

### Evaluation

```bash
python scripts/evaluate_model.py --model-path models/best.pt
```

### Export to ONNX

```bash
python scripts/export_model.py --format onnx
```

See [training/README.md](training/README.md) for detailed instructions.

## 📍 Geolocation Handling

### Real GPS Data

When sonar files contain navigation metadata:

- Extracted automatically
- Associated with each detection
- Displayed on map

### Manual Input

Users can manually enter coordinates:

- Clearly labeled "MANUALLY ASSIGNED LOCATION"
- Stored separately in database
- Never mixed with automated data

### Unavailable Data

When GPS metadata is missing:

```
"Geolocation unavailable because required navigation metadata
was not found."
```

No fabricated coordinates under any circumstances.

## 🤖 Local AI Assistant (Phase 17)

The AI Assistant is a **local, deterministic, rule-based** engine. It answers natural-language questions by matching intents against the **real SQLite detection database**. It does **not** use any external LLM.

### Capabilities

- Survey summarization
- Inspection recommendation ("What should I inspect first?")
- Detection explanation
- Confirmed / Possible / Priority queries
- Grounded references to stored detections

### Constraints

The assistant is **not** the detection engine. YOLOv8 is the source of truth. The assistant only queries, summarizes, and explains existing stored data — it never invents detection results or metrics.

### Provider Configuration

```bash
# In .env (recommended for full-local mode):
LLM_PROVIDER=disabled
```

The assistant works with `LLM_PROVIDER=disabled`. No API key, no Ollama, no external LLM and no network access are required. See [docs/phase17.md](docs/phase17.md).

## 📊 Dashboard Features

### Overview Page

- Total files processed
- Total detections
- Confirmed/Possible/Rejected breakdown
- High priority count
- Average confidence

### Detection Results

- Image viewer (original, processed, overlay)
- Bounding boxes with class labels
- Confidence percentages
- Status indicators

### Map Visualization

- Interactive Leaflet map
- Real geolocations only
- Filters: class, confidence, priority, date
- Cluster markers for dense areas

### Reports

Export filtered detections as:

- **CSV**: Spreadsheet-compatible format
- **JSON**: Machine-readable format
- Options: all detections, filtered, high-priority

### AI Assistant

- Natural language queries
- Survey questions
- Cleanup recommendations
- Report summarization

### Model Training UI

- Dataset upload
- Training parameter configuration
- Real-time metrics
- Model versioning

## 🔐 Security & Secrets

### Never Hardcoded

- API keys (OpenAI, etc.)
- Database passwords
- Secret tokens
- Credentials

### Secret Management

```bash
# .env.example contains TEMPLATES only
cp .env.example .env

# .env is NEVER committed (see .gitignore)
# Fill with real values locally only

# Check before commit:
python scripts/check_repo.py
```

### Pre-commit Safety Check

```bash
python scripts/check_repo.py
```

This detects:

- Accidentally committed .env files
- Exposed API keys
- Large raw data files
- Model weight files

Output: PASS or WARNING

## 🧪 Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=backend tests/

# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/
```

Tests cover:

- Data validation
- Preprocessing
- Detection parsing
- Shadow analysis
- False-positive filtering
- Priority scoring
- Database operations
- API endpoints

## 📚 Documentation

Detailed docs available in `/docs`:

- [architecture.md](docs/architecture.md) - System design
- [ai_pipeline.md](docs/ai_pipeline.md) - Detailed ML pipeline
- [dataset.md](docs/dataset.md) - Dataset preparation guide
- [geolocation.md](docs/geolocation.md) - GPS handling
- [llm.md](docs/llm.md) - LLM integration guide
- [api.md](docs/api.md) - REST API reference
- [deployment.md](docs/deployment.md) - Production deployment
- [hackathon_demo.md](docs/hackathon_demo.md) - Demo instructions

## 🐳 Docker Deployment

### Using Docker Compose

```bash
docker-compose up -d
```

Services:

- **backend**: FastAPI on port 8000
- **frontend**: React on port 5173
- **db**: SQLite volume

### Local Development (Recommended)

Follow "Quick Start" section above.

## 🚀 GitHub Setup

### Initial Commit

```bash
git init
git add .
git commit -m "Initial project setup: Phase 1 - GitHub-ready structure"
git branch -M main
git remote add origin <YOUR_REPOSITORY_URL>
git push -u origin main
```

### Before Committing

```bash
# Safety check for secrets/large files
python scripts/check_repo.py

# Should output: PASS
```

### What IS Committed

✅ Source code
✅ Configuration templates (.env.example)
✅ Documentation
✅ Test files
✅ Small demo assets
✅ .gitignore

### What IS NOT Committed (Intentionally Ignored)

❌ .env (real secrets)
❌ data/raw/ (large raw sonar files)
❌ models/\*.pt (large model weights)
❌ data/processed/ (generated files)
❌ data/exports/ (generated reports)
❌ venv/ (virtual environment)
❌ node_modules/ (frontend dependencies)

### Setting Up Locally

**For Raw Data:**

```bash
# Clone repository
git clone <url>

# Create data directories
mkdir -p data/raw
mkdir -p data/processed

# Place your sonar files in data/raw/
# The README in data/raw explains this:
# "These files are processed locally and intentionally
#  ignored by Git. Place real sonar measurements here."
```

**For Model Weights:**

```bash
# models/README.md explains:
# "Download or place trained weights here.
#  This directory is intentionally ignored by Git.
#  Configure MODEL_PATH in .env if using external storage."
```

## 📋 Checklist for Production

- [ ] Replace sample values in .env
- [ ] Configure database (SQLite or PostgreSQL)
- [ ] Set up LLM provider (or disable)
- [ ] Place trained model in models/
- [ ] Prepare real sonar dataset
- [ ] Configure file upload directory
- [ ] Set secure SECRET_KEY
- [ ] Enable HTTPS for production
- [ ] Set up monitoring/logging
- [ ] Backup database strategy
- [ ] Plan model update procedure

## 🔬 Demo Mode

Application includes a demo mode for testing without real hardware:

```bash
# In .env:
DEMO_MODE=true
DEMO_DATA_PATH=./data/demo
```

Demo assets are clearly marked. The system displays:

```
⚠️ DEMO MODE
```

When using demonstration data, never representing demo as real measurements.

## 📈 Real Metrics Only

This project maintains strict data integrity:

- ✅ Real YOLOv8 metrics from actual training
- ❌ NO fabricated accuracy numbers
- ✅ Real shadow analysis heuristics
- ❌ NO invented detection results
- ✅ Real GPS data from metadata
- ❌ NO fake coordinates
- ✅ Transparent priority scoring
- ❌ NO undocumented weighting

Every feature either works with real data or clearly reports why it cannot operate.

## 🔄 Development Roadmap

### ✅ PHASE 1: Foundation (COMPLETE)

- Project structure
- GitHub-ready files
- Configuration templates
- Documentation skeleton

### ✅ PHASES 2–20 (COMPLETE)

The full roadmap (ingestion → validation → preprocessing → YOLO → shadow → filtering → geolocation → database → priority → size → reports → dashboard → interactive map → local AI assistant → model management + ONNX → testing → final integration & SIH demo) is complete. See [docs/phase20.md](docs/phase20.md) for the final integration report and SIH demo workflow.

## 🎪 SIH Demo Workflow

1. Start backend: `uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000`
2. Start frontend: `npm run dev` (in `frontend/`)
3. Open the dashboard → upload a sonar image → show ingestion/validation/preprocessing
4. Run YOLO inference → show detected object + acoustic shadow evidence
5. Show CONFIRMED / POSSIBLE / REJECTED result and cleanup priority
6. Add geolocation → marker appears on the Interactive Map (Leaflet + OpenStreetMap, no API key)
7. Ask the Local AI Assistant: "What should I inspect first?"
8. Open Model Management → show active model / version
9. Generate a report (CSV / JSON)

Full details in [docs/phase20.md](docs/phase20.md). The project is fully local and ready for a local SIH presentation.

## 📝 License

Project licensed under [License Type - To Be Added]

## 👥 Contributing

For hackathon or community contributions:

1. Fork repository
2. Create feature branch
3. Follow code style (Black, isort, flake8)
4. Add tests for new features
5. Run pre-commit safety check
6. Submit pull request

## 📞 Support

For issues, questions, or suggestions:

- Create GitHub Issue
- Check documentation in `/docs`
- Review API docs at `/api/docs`

## 🎯 Key Design Principles

1. **No Fake Data**: Only real data or clear "unavailable" messages
2. **Transparency**: All scores and decisions are documented
3. **Modularity**: Services can be swapped or disabled independently
4. **Scalability**: Ready for multi-GPU training and PostgreSQL
5. **Security**: Secrets protected, no hardcoded credentials
6. **Testing**: Comprehensive test coverage for reliability
7. **Documentation**: Every feature documented with usage examples

---

**Built for hackathons, research, and production deployment.**

_Last Updated: 2026-09-04_
_Phase: 20 - Final Integration & SIH Demo (Complete)_
