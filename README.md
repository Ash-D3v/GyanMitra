# GyanMitra - NCERT Doubt Solver

A comprehensive AI-powered educational assistant that helps students solve doubts from NCERT textbooks using Retrieval-Augmented Generation (RAG). The system supports multiple languages (English, Hindi, Marathi, Urdu,etc) and provides accurate, citation-backed answers from official NCERT textbook content.

## 🎯 Project Overview

GyanMitra is a full-stack educational application that combines:
- **RAG (Retrieval-Augmented Generation)** pipeline for accurate textbook-based answers
- **Mistral-7B** language model for intelligent response generation
- **Multilingual support** for diverse student populations
- **Mobile-first design** with React Native/Expo
- **Citation system** that references specific textbook pages and chapters

The system processes student queries, retrieves relevant content from NCERT textbooks using semantic search, and generates grade-appropriate answers with proper citations.

## 📸 Screenshots

<div align="center">

![GyanMitra Screenshot 1](image/WhatsApp%20Image%202025-12-27%20at%2023.17.05.jpeg)
![GyanMitra Screenshot 2](image/WhatsApp%20Image%202025-12-27%20at%2023.17.07.jpeg)
![GyanMitra Screenshot 3](image/WhatsApp%20Image%202025-12-27%20at%2023.17.08.jpeg)
![GyanMitra Screenshot 4](image/WhatsApp%20Image%202025-12-27%20at%2023.17.29.jpeg)
![GyanMitra Screenshot 5](image/WhatsApp%20Image%202025-12-27%20at%2023.17.33.jpeg)

</div>

## 🏗️ Architecture

The project follows a microservices architecture with three main components:

### 1. **Python AI Service** (RAG Pipeline)
- **Location**: `ncert-doubt-solver-opea/ncert-doubt-solver-opea copy 2/`
- **Technology**: FastAPI, Mistral-7B, ChromaDB, Sentence Transformers
- **Purpose**: Handles query processing, vector retrieval, and LLM-based answer generation
- **Port**: 8000
- **Key Directories**: `opea_microservices/`, `scripts/`, `data/`, `models/`

### 2. **Node.js Backend API**
- **Location**: `GyanMitra/server/`
- **Technology**: Express.js, MongoDB, JWT Authentication
- **Purpose**: User management, conversation history, authentication, API orchestration
- **Port**: 3003

### 3. **React Native Mobile App**
- **Location**: `GyanMitra/gyanmitra-mobile/`
- **Technology**: React Native, Expo, TypeScript
- **Purpose**: User interface for students to ask questions and receive answers

## 📋 Prerequisites

Before installation, ensure you have the following installed:

### System Requirements
- **Python**: 3.8 or higher
- **Node.js**: 18.x or higher
- **npm** or **yarn**: Latest version
- **MongoDB**: 5.0 or higher (local or cloud instance)
- **Git**: For cloning the repository

### Hardware Requirements (for LLM)
- **Minimum**: 8GB RAM, CPU-only inference (slower)
- **Recommended**: 16GB+ RAM, GPU with Metal support (M2 Mac) or CUDA (NVIDIA GPU)
- **Storage**: At least 10GB free space for models and vector database

### Additional Dependencies
- **Tesseract OCR**: Required for PDF processing (if processing new textbooks)
  ```bash
  # macOS
  brew install tesseract
  
  # Ubuntu/Debian
  sudo apt-get install tesseract-ocr
  
  # Windows
  # Download from: https://github.com/UB-Mannheim/tesseract/wiki
  ```

## 🚀 Installation Guide

### Step 1: Clone the Repository

```bash
git clone https://github.com/Rudee007/GyanMitra.git
cd "ncert-doubt-solver-opea copy 3"
```

### Step 2: Python Environment Setup

1. **Create a virtual environment** (recommended):

```bash
# Using venv
python3 -m venv venv

# Activate virtual environment
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

2. **Install Python dependencies**:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

3. **Install llama-cpp-python with Metal support** (for M2 Mac):

```bash
# For Apple Silicon (M1/M2) with Metal acceleration
CMAKE_ARGS="-DLLAMA_METAL=on" pip install llama-cpp-python

# For CPU-only (slower, but works everywhere)
pip install llama-cpp-python
```

### Step 3: Download Mistral-7B Model

The system requires the Mistral-7B-Instruct model in GGUF format. Download it manually:

1. **Download the model**:
   - Visit: https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF
   - Download: `mistral-7b-instruct-v0.2.Q4_K_M.gguf` (approximately 4.1 GB)
   - Recommended quantization: `Q4_K_M` (good balance of quality and speed)

2. **Place the model file**:
   ```bash
   mkdir -p models
   # Move the downloaded .gguf file to:
   # models/mistral-7b-instruct-v0.2.gguf
   ```

3. **Verify model path**:
   The model should be located at: `models/mistral-7b-instruct-v0.2.gguf`

### Step 4: Vector Database Setup

The vector database contains embedded NCERT textbook content. If you need to rebuild it:

1. **Ensure embedding data exists**:
   - Check for files in `data/processed/embeddings/`
   - Required files:
     - `6_science_english_embedded.json`
     - `ncert_hindi_ocr_embedded.json` (or similar)

2. **Rebuild vector store** (if needed):
   ```bash
   # Navigate to the Python service directory first
   cd "ncert-doubt-solver-opea/ncert-doubt-solver-opea copy 2"
   python scripts/rebuild_vector_store_multilingual.py
   ```
   This script will:
   - Load existing embedded chunks
   - Generate new multilingual embeddings using `intfloat/multilingual-e5-large`
   - Create/update the ChromaDB vector store at `data/chroma_db/`

3. **Verify vector store**:
   The vector database should be located at: `data/chroma_db/`

### Step 5: Node.js Backend Setup

1. **Navigate to server directory**:
   ```bash
   cd GyanMitra/server
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Create environment file**:
   Create a `.env` file in `GyanMitra/server/` with the following content:
   
   ```env
   # MongoDB Connection (uncomment and configure)
   MONGO_URI=mongodb://localhost:27017/GyanMitra
   # Or use MongoDB Atlas:
   # MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/GyanMitra
   
   # Server Configuration
   PORT=3003
   NODE_ENV=development
   
   # Frontend URL (for email verification links)
   FRONTEND_URL=http://localhost:5173
   
   # JWT Secret (generate a random string)
   JWT_SECRET=your-super-secret-jwt-key-change-this-in-production
   
   # Email Configuration (for verification)
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=465
   SMTP_SECURE=true
   SMTP_USER=your-email@gmail.com
   SMTP_PASS=your-app-password
   
   # Google OAuth (optional)
   GOOGLE_CLIENT_ID=your-google-client-id
   
   # AI Service Configuration
   AI_SERVICE_URL=http://localhost:8000
   USE_MOCK_AI=false
   ```

4. **Start MongoDB** (if running locally):
   ```bash
   # macOS (using Homebrew)
   brew services start mongodb-community

   # Linux
   sudo systemctl start mongod

   # Or use MongoDB Atlas (cloud) - no local installation needed
   ```

### Step 6: React Native Mobile App Setup

1. **Navigate to mobile app directory**:
   ```bash
   cd GyanMitra/gyanmitra-mobile
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Configure API endpoint**:
   Edit `GyanMitra/gyanmitra-mobile/constants/Config.ts` and update the `YOUR_LOCAL_IP` variable in the `getApiBaseUrl()` function:
   ```typescript
   function getApiBaseUrl(): string {
     const PORT = 3003;
     const YOUR_LOCAL_IP = 'YOUR_COMPUTER_IP'; // Update this with your local IP
     
     if (__DEV__) {
       return `http://${YOUR_LOCAL_IP}:${PORT}/api`;
     }
     
     return 'https://your-production-url.com/api';
   }
   ```
   
   **To find your local IP:**
   - **macOS/Linux**: Run `ifconfig | grep "inet "` or `ipconfig getifaddr en0`
   - **Windows**: Run `ipconfig` and look for IPv4 Address
   - **Android Emulator**: Use `10.0.2.2` instead of localhost


4. **Install Expo CLI** (if not already installed):
   ```bash
   npm install -g expo-cli
   ```

## 🎮 Running the Application

### Start All Services

You need to run three services simultaneously:

#### Terminal 1: Python AI Service (RAG API)

```bash
# Navigate to the Python service directory
cd "ncert-doubt-solver-opea/ncert-doubt-solver-opea copy 2"

# Activate virtual environment (if not already active)
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows

# Start FastAPI server
python scripts/api_server.py

# Or using uvicorn directly:
uvicorn scripts.api_server:app --host 0.0.0.0 --port 8000 --reload
```

**Verify**: Visit http://localhost:8000/docs to see the API documentation.

#### Terminal 2: Node.js Backend

```bash
cd GyanMitra/server
npm run dev
# Or: node server.js
```

**Verify**: Visit http://localhost:3003/api/health to check server status.

#### Terminal 3: React Native Mobile App

```bash
cd GyanMitra/gyanmitra-mobile
npm start
# Or: expo start
```

Then:
- Press `i` for iOS Simulator (macOS only)
- Press `a` for Android Emulator
- Scan QR code with Expo Go app on your phone

## 🔧 Configuration

### Python AI Service Configuration

Edit `config/mistral_optimization.yaml` to adjust:
- Model parameters (temperature, top_p, top_k)
- Context window size
- GPU/CPU settings
- Vector database settings

### Model Configuration

The Mistral service configuration is in `opea_microservices/llm/mistral_service.py`:

```python
@dataclass
class MistralConfig:
    model_path: str = "../models/mistral-7b-instruct-v0.2.gguf"
    n_ctx: int = 4096  # Context window
    n_threads: int = 8  # CPU threads
    n_gpu_layers: int = 35  # Metal acceleration (M2 Mac)
    temperature: float = 0.3
    top_p: float = 0.95
    top_k: int = 40
    max_tokens: int = 512
```

### Embedding Model

The system uses `intfloat/multilingual-e5-large` (1024 dimensions) for multilingual support. This model:
- Supports English, Hindi, and other languages
- Provides high-quality semantic embeddings
- Requires ~2GB RAM when loaded

To change the embedding model, update:
- `scripts/api_server.py` (line 131)
- `opea_microservices/orchestration/rag_orchestrator.py` (default parameter)

## 📚 Data Processing Pipeline

The system includes notebooks for processing NCERT textbooks:

1. **OCR Extraction** (`notebooks/01_ocr_extraction.ipynb`):
   - Extracts text from PDF textbooks using OCR
   - Handles both English and Hindi content

2. **Chunking & Metadata** (`notebooks/02_chunking_metadata.ipynb`):
   - Splits text into semantic chunks
   - Adds metadata (grade, subject, chapter, page number)

3. **Embeddings & Vector DB** (`notebooks/03_embeddings_vectordb.ipynb`):
   - Generates embeddings for all chunks
   - Stores in ChromaDB vector database

## 🔐 Environment Variables

### Python Service
No environment variables required (uses default paths). Optional:
- `MODEL_PATH`: Override model path
- `VECTOR_DB_PATH`: Override vector database path

### Node.js Backend
Required in `GyanMitra/server/.env`:
- `MONGO_URI`: MongoDB connection string (required)
- `PORT`: Server port (default: 3003)
- `NODE_ENV`: Environment mode - "development" or "production"
- `FRONTEND_URL`: Frontend URL for email verification links
- `JWT_SECRET`: Secret for JWT token signing (required)
- `SMTP_HOST`: SMTP server hostname (e.g., "smtp.gmail.com")
- `SMTP_PORT`: SMTP port (465 for SSL, 587 for TLS)
- `SMTP_SECURE`: "true" for SSL (port 465) or "false" for TLS (port 587)
- `SMTP_USER`: Email address for sending verification emails
- `SMTP_PASS`: Email app password or key
- `GOOGLE_CLIENT_ID`: Google OAuth client ID (optional)
- `AI_SERVICE_URL`: Python AI service URL (default: http://localhost:8000)
- `USE_MOCK_AI`: "true" to use mock AI responses, "false" to use real AI service

### Mobile App
No environment variables (configured in `constants/Config.ts`).

## 🧪 Testing the System

### Test Python AI Service

```bash
# Health check
curl http://localhost:8000/health

# Test query
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is photosynthesis?",
    "grade": 6,
    "subject": "science",
    "language": "english"
  }'
```

### Test Node.js Backend

```bash
# Health check
curl http://localhost:3003/api/health

# Test authentication (after creating a user)
curl -X POST "http://localhost:3003/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

### Interactive RAG Testing

```bash
# Navigate to the Python service directory first
cd "ncert-doubt-solver-opea/ncert-doubt-solver-opea copy 2"

# Run interactive chat mode
python scripts/run_rag_with_mistral.py --mode interactive

# Single query
python scripts/run_rag_with_mistral.py --mode single \
  --question "What is photosynthesis?" \
  --grade 6 \
  --subject science
```

## 🐛 Troubleshooting

### Model Not Found Error

**Error**: `FileNotFoundError: Model not found at models/mistral-7b-instruct-v0.2.gguf`

**Solution**:
1. Download the model from HuggingFace (see Step 3 in Installation)
2. Ensure the file is named exactly: `mistral-7b-instruct-v0.2.gguf`
3. Place it in the `models/` directory

### Vector Database Empty

**Error**: No results returned from queries

**Solution**:
1. Check if `data/chroma_db/` exists and contains data
2. Navigate to `ncert-doubt-solver-opea/ncert-doubt-solver-opea copy 2` and rebuild vector store: `python scripts/rebuild_vector_store_multilingual.py`
3. Verify embedding files exist in `data/processed/embeddings/`

### GPU Acceleration Not Working

**Error**: Model runs slowly on M2 Mac

**Solution**:
1. Reinstall llama-cpp-python with Metal support:
   ```bash
   pip uninstall llama-cpp-python
   CMAKE_ARGS="-DLLAMA_METAL=on" pip install llama-cpp-python
   ```
2. Verify `n_gpu_layers` is set to 35 in `MistralConfig`

### MongoDB Connection Error

**Error**: `Error connecting to DB`

**Solution**:
1. Verify MongoDB is running: `mongosh` or check service status
2. Check `MONGO_URI` in `.env` file
3. For MongoDB Atlas, ensure IP whitelist includes your IP

### Mobile App Cannot Connect to Backend

**Error**: Network error in mobile app

**Solution**:
1. Update `YOUR_LOCAL_IP` in `constants/Config.ts` to your computer's local IP
2. Ensure all devices are on the same network
3. Check firewall settings (port 3003 should be open)
4. For Android emulator, use `10.0.2.2` instead of localhost

### AI Service Timeout

**Error**: Request timeout when querying

**Solution**:
1. Increase timeout in `GyanMitra/server/src/services/aiService.js` (TIMEOUT constant)
2. Check if model is loading correctly (check Python service logs)
3. Reduce `top_k` parameter to retrieve fewer chunks

## 📖 API Documentation & Routes

### Python AI Service (FastAPI) - Port 8000

**Base URL**: `http://localhost:8000`

**Interactive Documentation**:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

#### Health & Info Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/` | API status and information | No |
| `GET` | `/health` | Health check endpoint | No |
| `GET` | `/model-info` | Get LLM model information | No |

**Example: Health Check**
```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "vector_store_ready": true,
  "llm_ready": true,
  "total_documents": 1234,
  "multilingual_support": true
}
```

#### RAG Query Endpoint

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/query` | Process query using RAG pipeline | No |

**Request Body:**
```json
{
  "query": "What is photosynthesis?",
  "grade": 6,
  "subject": "science",
  "language": "english",
  "top_k": 3
}
```

**Request Parameters:**
- `query` (string, required): Student's question (any language)
- `grade` (integer, required): Grade level (5-10)
- `subject` (string, required): Subject name (e.g., "science", "mathematics")
- `language` (string, optional): Response language - "english" or "hindi" (default: "english")
- `top_k` (integer, optional): Number of chunks to retrieve (default: 3)

**Response:**
```json
{
  "answer": "Photosynthesis is the process by which plants...",
  "metadata": {
    "grade": 6,
    "subject": "science",
    "language": "english",
    "query_language": "english",
    "model": "Mistral-7B-Instruct-v0.2",
    "tokens_used": 512,
    "confidence": 0.85,
    "chunks_retrieved": 3,
    "processing_time_ms": 1234
  },
  "citations": [
    {
      "id": 1,
      "source": "NCERT Science Grade 6",
      "chapter": "Getting to Know Plants",
      "section": "Photosynthesis",
      "page": 45,
      "excerpt": "Photosynthesis is the process...",
      "relevance": 0.92,
      "chunk_id": "chunk_123"
    }
  ],
  "source_chunks": [...]
}
```

**Example Request:**
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is photosynthesis?",
    "grade": 6,
    "subject": "science",
    "language": "english",
    "top_k": 3
  }'
```

---

### Node.js Backend API - Port 3003

**Base URL**: `http://localhost:3003/api`

#### Health Endpoint

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/api/health` | Server health check | No |

**Example:**
```bash
curl http://localhost:3003/api/health
```

**Response:**
```json
{
  "status": "ok",
  "service": "GyanMitra Backend",
  "timestamp": "2025-01-27T12:00:00.000Z",
  "port": 3003,
  "database": "connected"
}
```

#### Authentication Routes (`/api/auth`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/api/auth/signup` | Register new user | No |
| `POST` | `/api/auth/login` | Login user | No |
| `POST` | `/api/auth/google` | Google OAuth authentication | No |
| `GET` | `/api/auth/verify` | Verify email address | No |
| `POST` | `/api/auth/resend-verification` | Resend verification email | No |
| `GET` | `/api/auth/check-verification` | Check verification status | No |

**Signup Request:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "securePassword123",
  "grade": 6,
  "preferredLanguage": "english"
}
```

**Login Request:**
```json
{
  "email": "john@example.com",
  "password": "securePassword123"
}
```

**Login Response:**
```json
{
  "success": true,
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "user_id",
    "name": "John Doe",
    "email": "john@example.com",
    "grade": 6,
    "preferredLanguage": "english"
  }
}
```

#### Query Routes (`/api/query`)

All query routes require authentication. Include JWT token in Authorization header: `Authorization: Bearer <token>`

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/api/query` | Submit a query (new or follow-up) | Yes |
| `GET` | `/api/query/health` | Check AI service health | Yes |
| `GET` | `/api/query/model-info` | Get AI model information | Yes |

**Submit Query Request:**
```json
{
  "query": "What is photosynthesis?",
  "grade": 6,
  "subject": "science",
  "language": "english",
  "conversationId": "optional_conversation_id"
}
```

**Submit Query Response:**
```json
{
  "success": true,
  "conversationId": "conv_123",
  "message": {
    "id": "msg_456",
    "query": "What is photosynthesis?",
    "answer": "Photosynthesis is the process...",
    "citations": [...],
    "timestamp": "2025-01-27T12:00:00.000Z"
  }
}
```

**Example:**
```bash
curl -X POST "http://localhost:3003/api/query" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "query": "What is photosynthesis?",
    "grade": 6,
    "subject": "science",
    "language": "english"
  }'
```

#### Conversation Routes (`/api/conversation`)

All conversation routes require authentication.

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/api/conversation` | Get list of user's conversations (paginated) | Yes |
| `GET` | `/api/conversation/:id` | Get specific conversation by ID | Yes |
| `DELETE` | `/api/conversation/:id` | Archive conversation (soft delete) | Yes |
| `PUT` | `/api/conversation/:id/restore` | Restore archived conversation | Yes |

**Query Parameters for GET `/api/conversation`:**
- `page` (integer, optional): Page number (default: 1)
- `limit` (integer, optional): Items per page (default: 20)
- `status` (string, optional): Filter by status (e.g., "active", "archived")
- `subject` (string, optional): Filter by subject
- `grade` (integer, optional): Filter by grade

**Example: Get Conversations**
```bash
curl -X GET "http://localhost:3003/api/conversation?page=1&limit=10" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Example: Get Specific Conversation**
```bash
curl -X GET "http://localhost:3003/api/conversation/conv_123" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

#### Feedback Routes (`/api/feedback`)

All feedback routes require authentication.

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/api/feedback` | Submit feedback on an AI response | Yes |
| `GET` | `/api/feedback/my-feedback` | Get user's own feedback history | Yes |
| `PUT` | `/api/feedback/:id` | Update user's feedback | Yes |
| `DELETE` | `/api/feedback/:id` | Delete user's feedback | Yes |

**Submit Feedback Request:**
```json
{
  "conversationId": "conv_123",
  "messageIndex": 0,
  "rating": 5,
  "comment": "Very helpful answer!"
}
```

**Query Parameters for GET `/api/feedback/my-feedback`:**
- `page` (integer, optional): Page number (default: 1)
- `limit` (integer, optional): Items per page (default: 20)
- `rating` (integer, optional): Filter by rating (1-5)

**Example: Submit Feedback**
```bash
curl -X POST "http://localhost:3003/api/feedback" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "conversationId": "conv_123",
    "messageIndex": 0,
    "rating": 5,
    "comment": "Very helpful!"
  }'
```

#### User Routes (`/api/users`)

All user routes require authentication.

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/api/users/profile` | Get current user's profile | Yes |
| `PUT` | `/api/users/profile` | Update current user's profile | Yes |

**Update Profile Request:**
```json
{
  "name": "John Doe",
  "grade": 7,
  "preferredLanguage": "hindi",
  "subjects": ["science", "mathematics"]
}
```

**Example: Get Profile**
```bash
curl -X GET "http://localhost:3003/api/users/profile" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Example: Update Profile**
```bash
curl -X PUT "http://localhost:3003/api/users/profile" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "name": "John Doe",
    "grade": 7,
    "preferredLanguage": "hindi"
  }'
```

---

### Authentication

Most endpoints require JWT authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

To get a token:
1. Register: `POST /api/auth/signup`
2. Login: `POST /api/auth/login`
3. Use the `token` from the response in subsequent requests

### Error Responses

All endpoints may return error responses in the following format:

```json
{
  "success": false,
  "error": "Error message here",
  "status_code": 400
}
```

**Common HTTP Status Codes:**
- `200`: Success
- `201`: Created
- `400`: Bad Request
- `401`: Unauthorized (missing or invalid token)
- `403`: Forbidden
- `404`: Not Found
- `500`: Internal Server Error
- `503`: Service Unavailable (AI service not ready)

## 🛠️ Development

### Project Structure

```
.
├── config/                 # Configuration files
│   └── mistral_optimization.yaml
├── data/                   # Data storage
│   ├── chroma_db/         # Vector database
│   └── processed/         # Processed embeddings
├── GyanMitra/
│   ├── gyanmitra-mobile/  # React Native app
│   └── server/            # Node.js backend
├── image/                  # Screenshots and images
├── ncert-doubt-solver-opea/
│   └── ncert-doubt-solver-opea copy 2/
│       ├── config/        # Configuration files
│       ├── data/          # Data storage
│       │   ├── chroma_db/ # Vector database
│       │   └── processed/ # Processed embeddings
│       ├── models/        # LLM model storage
│       ├── notebooks/     # Jupyter notebooks for data processing
│       ├── opea_microservices/  # Python microservices
│       │   ├── llm/       # Mistral LLM service
│       │   ├── orchestration/  # RAG orchestrator
│       │   └── retrieval/ # Vector store service
│       └── scripts/       # Utility scripts
│           ├── api_server.py  # FastAPI server
│           └── run_rag_with_mistral.py
```

### Adding New Textbooks

1. Navigate to `ncert-doubt-solver-opea/ncert-doubt-solver-opea copy 2/`
2. Place PDF files in a designated folder
3. Run OCR extraction notebook: `notebooks/01_ocr_extraction.ipynb`
4. Run chunking notebook: `notebooks/02_chunking_metadata.ipynb`
5. Run embeddings notebook: `notebooks/03_embeddings_vectordb.ipynb`
6. Rebuild vector store: `python scripts/rebuild_vector_store_multilingual.py`

### Customizing the LLM

To use a different model:
1. Download GGUF format model
2. Update `MistralConfig` in `opea_microservices/llm/mistral_service.py`
3. Adjust model path and parameters
4. Update system prompts if needed

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

**Note on Educational Content**: The NCERT textbook content used in this project is the property of the National Council of Educational Research and Training (NCERT), India. This project is intended for educational purposes only. Users are responsible for ensuring compliance with NCERT's terms of use for their content.

**Third-Party Models**:
- **Mistral-7B**: Licensed under Apache 2.0 License
- **Embedding Models**: Check individual model licenses on HuggingFace
- **Other Dependencies**: See `requirements.txt` and `package.json` files for respective licenses

## 🤝 Contributing

We welcome contributions to GyanMitra! Whether you're fixing bugs, adding features, improving documentation, or enhancing the AI models, your help is appreciated.

### How to Contribute

1. **Fork the Repository**
   - Click the "Fork" button on GitHub
   - Clone your fork: `git clone https://github.com/Rudee007/GyanMitra.git`

2. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

3. **Make Your Changes**
   - Follow the existing code style and conventions
   - Add comments for complex logic
   - Update documentation if needed
   - Test your changes thoroughly

4. **Commit Your Changes**
   ```bash
   git commit -m "Add: Description of your changes"
   ```
   - Use clear, descriptive commit messages
   - Follow conventional commit format when possible (e.g., `Add:`, `Fix:`, `Update:`)

5. **Push and Create Pull Request**
   ```bash
   git push origin feature/your-feature-name
   ```
   - Create a pull request on GitHub
   - Provide a clear description of your changes
   - Reference any related issues

### Contribution Guidelines

#### Code Style
- **Python**: Follow PEP 8 style guide
- **JavaScript/TypeScript**: Use ESLint configuration provided
- **React Native**: Follow React Native best practices
- Use meaningful variable and function names
- Add docstrings/comments for complex functions

#### Testing
- Test your changes locally before submitting
- Ensure all services (Python API, Node.js backend, mobile app) work together
- Test with both English and Hindi queries if applicable
- Verify vector database operations work correctly

#### Documentation
- Update README.md if you add new features or change installation steps
- Add comments to complex code sections
- Update API documentation if endpoints change
- Include examples in your PR description

#### Areas for Contribution

- **Bug Fixes**: Fix issues reported in GitHub Issues
- **New Features**: Add requested features or propose new ones
- **Documentation**: Improve README, add code comments, create tutorials
- **Performance**: Optimize model inference, improve vector search speed
- **Multilingual Support**: Add support for more languages (Marathi, Urdu, etc.)
- **UI/UX**: Improve mobile app interface and user experience
- **Testing**: Add unit tests, integration tests, or end-to-end tests
- **Data Processing**: Improve OCR accuracy, chunking strategies, or embeddings

#### Reporting Issues

When reporting bugs or requesting features:
- Use the GitHub Issues tab
- Provide a clear title and description
- Include steps to reproduce (for bugs)
- Add relevant logs or error messages
- Specify your environment (OS, Python version, Node version, etc.)

#### Code Review Process

1. All pull requests will be reviewed by maintainers
2. Address any feedback or requested changes
3. Once approved, your PR will be merged
4. Thank you for contributing! 🎉

### Development Setup

Before contributing, ensure you can:
- Run all three services locally
- Test queries in the mobile app
- Process new textbook data (if working on data pipeline)
- Rebuild the vector database

### Questions?

If you have questions about contributing:
- Open a GitHub Discussion
- Check existing Issues and Pull Requests
- Review the codebase to understand the architecture

Thank you for helping make GyanMitra better for students everywhere! 🌟

## 📧 Support

For issues and questions:
- Check the troubleshooting section
- Review API documentation at `/docs` endpoints
- Check logs in terminal outputs

## 🎓 Acknowledgments

- Mistral AI for the Mistral-7B model
- ChromaDB for vector database
- Sentence Transformers for embeddings
- NCERT for educational content
