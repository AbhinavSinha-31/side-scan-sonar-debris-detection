# Documentation Index

Quick navigation to all project documentation.

## 📋 Main Documentation

- **[README.md](README.md)** - Complete project overview, features, architecture, quick start, and troubleshooting
- **[docs/architecture.md](docs/architecture.md)** - System architecture and module descriptions

## 🗂️ Component Documentation

### Backend
- **[backend/README.md](backend/README.md)** - Backend structure, API endpoints, database setup, and services

### Frontend
- **[frontend/README.md](frontend/README.md)** - React/Vite setup, components, styling, and integration

### Training Pipeline
- **[training/README.md](training/README.md)** - YOLOv8 training, dataset preparation, model versioning

### Models
- **[models/README.md](models/README.md)** - Model storage, versioning, ONNX export

## 📊 Data Management

### Raw Data
- **[data/raw/README.md](data/raw/README.md)** - Where to place raw sonar files

### Processed Data
- **[data/processed/README.md](data/processed/README.md)** - Generated files and cleanup

### Demo Data
- **[data/demo/README.md](data/demo/README.md)** - Demonstration assets disclaimer

### Exports
- **[data/exports/README.md](data/exports/README.md)** - Generated reports and backups

## 🔧 Configuration

- **[.env.example](.env.example)** - Template configuration file with all variables documented
- **[.gitignore](.gitignore)** - Git ignore patterns for security and cleanliness

## 🚀 Getting Started

1. **First time setup?** → Start with [README.md](README.md) "Quick Start" section
2. **Backend development?** → See [backend/README.md](backend/README.md)
3. **Frontend development?** → See [frontend/README.md](frontend/README.md)
4. **Training models?** → See [training/README.md](training/README.md)
5. **Deploying?** → See [docs/deployment.md](docs/deployment.md) (Phase 20+)

## 📚 Detailed Guides (Phase 2+)

These documents will be created in subsequent phases:

- `docs/ai_pipeline.md` - Detailed AI detection pipeline
- `docs/dataset.md` - Dataset preparation and annotation
- `docs/geolocation.md` - GPS and geospatial handling
- `docs/llm.md` - LLM integration and assistant features
- `docs/api.md` - Complete REST API reference
- `docs/deployment.md` - Production deployment guide
- `docs/hackathon_demo.md` - Demonstration instructions

## 🔐 Security

- **Secret Management** - See "Secret Management" in [README.md](README.md)
- **Pre-commit Check** - Run `python scripts/check_repo.py` before git push
- **Environment Variables** - See [.env.example](.env.example)

## 🧪 Testing

- Unit tests: `tests/unit/`
- Integration tests: `tests/integration/`
- See "Testing" in [README.md](README.md) for commands

## 📖 Phase Overview

**Phase 1** (Foundation) ✅

**Phase 2-19** (Implementation) ✅

**Phase 20** (Final Integration & SIH Demo) ✅ — see [docs/phase20.md](docs/phase20.md)

The complete 20-phase roadmap (ingestion → validation → preprocessing → YOLO → shadow → filtering → geolocation → database → priority → size → reports → dashboard → interactive map → local AI assistant → model management → testing → final integration) is implemented and verified. The project runs fully locally on the user's laptop.

## 💡 Quick Reference

| Topic | Location |
|-------|----------|
| Project Overview | [README.md](README.md) |
| Architecture | [docs/architecture.md](docs/architecture.md) |
| Backend Setup | [backend/README.md](backend/README.md) |
| Frontend Setup | [frontend/README.md](frontend/README.md) |
| Training | [training/README.md](training/README.md) |
| API Endpoints | [backend/README.md](backend/README.md) |
| Environment Config | [.env.example](.env.example) |
| Data Handling | [data/raw/README.md](data/raw/README.md) |
| Git Setup | [README.md](README.md) - GitHub Setup section |
| Security | [README.md](README.md) - Security section |

## 🆘 Troubleshooting

See "Troubleshooting" sections in:
- [README.md](README.md) - General issues
- [backend/README.md](backend/README.md) - Backend-specific
- [frontend/README.md](frontend/README.md) - Frontend-specific
- [training/README.md](training/README.md) - Training issues

## 📞 Support

- **Questions?** Check relevant README first
- **Found a bug?** Check troubleshooting section
- **Need help?** Review [docs/architecture.md](docs/architecture.md)

---

**Last Updated**: 2026-09-04  
**Phase**: 20 - Final Integration & SIH Demo ✅
