# Multi-Agent Code Generator - Refactored Architecture

A sophisticated multi-agent framework that transforms natural language descriptions into complete Python applications using specialized AI agents. This project has been refactored to separate business logic from the frontend using a FastAPI backend and clean Streamlit frontend.

## 🏗️ Architecture Overview

The system now follows a clean separation of concerns with a backend/frontend architecture:

```
┌─────────────────┐    HTTP/WebSocket    ┌─────────────────┐
│                 │ ◄─────────────────► │                 │
│  Streamlit UI   │                     │  FastAPI Backend│
│   (Frontend)    │                     │   (Business     │
│                 │                     │     Logic)      │
└─────────────────┘                     └─────────────────┘
                                                │
                                                ▼
                                        ┌─────────────────┐
                                        │   AutoGen       │
                                        │   Agents        │
                                        │                 │
                                        └─────────────────┘
```

### Backend (FastAPI)
- **API Layer**: RESTful endpoints with automatic OpenAPI documentation
- **Service Layer**: Business logic for pipeline, agents, progress, and projects
- **Core Logic**: Multi-agent pipeline orchestration and agent management
- **Real-time Updates**: WebSocket support for live progress tracking

### Frontend (Streamlit)
- **UI Only**: Clean separation with no business logic
- **API Client**: HTTP client for backend communication
- **Real-time UI**: Progress tracking and live updates
- **User Experience**: Intuitive interface for code generation

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- All dependencies from `requirements.txt`

### Installation
```bash
# Install dependencies
pip install -r requirements.txt
```

### Running the Application

#### Option 1: Using Startup Scripts (Recommended)
```bash
# Terminal 1: Start the backend
python start_backend.py

# Terminal 2: Start the frontend
python start_frontend.py
```

#### Option 2: Manual Startup
```bash
# Terminal 1: Start FastAPI backend
cd backend
python main.py
# Backend available at: http://localhost:8000
# API docs available at: http://localhost:8000/docs

# Terminal 2: Start Streamlit frontend
cd frontend
streamlit run streamlit_app.py
# Frontend available at: http://localhost:8501
```

## 📁 Project Structure

```
Multi-Agent-Code/
├── backend/                    # FastAPI Backend
│   ├── main.py                # FastAPI app entry point
│   ├── api/                   # API layer
│   │   ├── routes/           # API route handlers
│   │   │   ├── pipeline.py   # Pipeline endpoints
│   │   │   ├── agents.py     # Agent endpoints
│   │   │   ├── progress.py   # Progress tracking + WebSocket
│   │   │   └── projects.py   # Project management
│   │   └── dependencies.py   # Dependency injection
│   ├── services/             # Business logic layer
│   │   ├── pipeline_service.py
│   │   ├── agent_service.py
│   │   ├── progress_service.py
│   │   └── project_service.py
│   ├── models/               # Pydantic models
│   │   ├── requests.py       # Request models
│   │   ├── responses.py      # Response models
│   │   └── schemas.py        # Data schemas
│   ├── core/                 # Core business logic
│   ├── agents/               # AutoGen agent definitions
│   └── config/               # Configuration
├── frontend/                  # Streamlit Frontend
│   ├── streamlit_app.py      # Main UI application
│   └── client/               # API client
│       └── api_client.py     # HTTP client for backend
├── start_backend.py          # Backend startup script
├── start_frontend.py         # Frontend startup script
├── requirements.txt          # Dependencies
└── README.md                 # This file
```

## 🔧 API Endpoints

### Pipeline Management
- `POST /api/v1/pipeline/generate` - Start code generation
- `POST /api/v1/pipeline/validate` - Validate user input
- `GET /api/v1/pipeline/status` - Get pipeline status
- `GET /api/v1/pipeline/status/{project_id}` - Get project status
- `POST /api/v1/pipeline/cancel/{project_id}` - Cancel project
- `GET /api/v1/pipeline/result/{project_id}` - Get project result

### Agent Information
- `GET /api/v1/agents/info` - Get all agent information
- `GET /api/v1/agents/{agent_name}` - Get specific agent details
- `GET /api/v1/agents/capabilities/{agent_name}` - Get agent capabilities

### Progress Tracking
- `GET /api/v1/progress/{project_id}` - Get project progress
- `GET /api/v1/progress/{project_id}/logs` - Get project logs
- `WebSocket /api/v1/progress/ws/{project_id}` - Real-time progress updates

### Project Management
- `GET /api/v1/projects/history` - Get project history
- `GET /api/v1/projects/statistics` - Get project statistics
- `GET /api/v1/projects/{project_id}` - Get project result
- `GET /api/v1/projects/search` - Search projects

## 🤖 Available Agents

1. **Requirement Analyst** - Analyzes natural language input and creates structured requirements
2. **Python Coder** - Generates high-quality Python code from requirements
3. **Code Reviewer** - Reviews code for quality, security, and best practices
4. **Documentation Writer** - Creates comprehensive documentation
5. **Test Generator** - Generates comprehensive test suites
6. **Deployment Engineer** - Creates deployment configurations and scripts
7. **UI Designer** - Creates Streamlit user interfaces

## 🔄 Pipeline Steps

1. **Requirements Analysis** - Convert natural language to structured requirements
2. **Code Generation** - Generate Python code from requirements
3. **Code Review & Iteration** - Review and improve code quality
4. **Documentation Generation** - Create comprehensive documentation
5. **Test Case Generation** - Generate test suites
6. **Deployment Configuration** - Create deployment configs
7. **UI Generation** - Create Streamlit user interface

## 🌟 Key Features

### Backend Features
- **Async/Await Support** - Full async support for better performance
- **WebSocket Support** - Real-time progress updates
- **Background Tasks** - Long-running pipeline execution
- **Auto-generated OpenAPI** - Automatic API documentation
- **CORS Support** - Enable frontend-backend communication
- **Error Handling** - Comprehensive error handling and logging

### Frontend Features
- **Clean UI** - Separation of concerns with no business logic
- **Real-time Updates** - Live progress tracking via API polling
- **Error Boundaries** - Graceful error handling and recovery
- **Download Support** - Download generated code and documentation
- **Project History** - View and manage previous generations

## 🔧 Development

### Backend Development
```bash
cd backend
python main.py
# API docs available at http://localhost:8000/docs
```

### Frontend Development
```bash
cd frontend
streamlit run streamlit_app.py
```

### Testing the API
Visit `http://localhost:8000/docs` for interactive API documentation and testing.

## 📊 Benefits of New Architecture

1. **Separation of Concerns** - Clear distinction between UI and business logic
2. **Scalability** - Backend can serve multiple frontends (web, mobile, CLI)
3. **Testability** - Business logic can be tested independently
4. **Maintainability** - Easier to maintain and extend each layer
5. **Performance** - Async backend with efficient resource utilization
6. **API Access** - External systems can integrate via REST API
7. **Real-time Updates** - WebSocket support for live progress tracking

## 🚀 Deployment

The refactored architecture supports various deployment options:

- **Development**: Run both services locally
- **Production**: Deploy backend and frontend separately
- **Docker**: Containerize each service independently
- **Cloud**: Deploy to cloud platforms with auto-scaling

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test both backend and frontend
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

## 🆘 Troubleshooting

### Backend Issues
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check if port 8000 is available
- Verify agent configurations in `backend/config/`

### Frontend Issues
- Ensure backend is running at `http://localhost:8000`
- Check if port 8501 is available
- Verify API client configuration

### Common Issues
- **Connection Refused**: Make sure backend is running before starting frontend
- **Import Errors**: Ensure you're running from the correct directory
- **Agent Errors**: Check your OpenAI API key and model configurations

For more help, check the API documentation at `http://localhost:8000/docs` when the backend is running.
