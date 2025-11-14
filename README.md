# Codebase Analyzer

A powerful AI-driven application that analyzes codebases and recreates them with logical Git structure, complete with feature branches, meaningful commits, and proper organization.

## Features

- 🔍 **Intelligent Analysis**: Uses AI to understand codebase structure and functionality
- 🌿 **Logical Git Structure**: Creates feature branches with meaningful commit history
- 📦 **Docker Containerized**: Runs as microservices with Docker Compose
- 🖥️ **CLI Interface**: Direct command-line tool for quick analysis
- 🌐 **REST API**: HTTP endpoints for integration with other systems
- 🔗 **Webhook Support**: Trigger analysis via webhooks with signature verification
- ⚡ **Async Processing**: Background job processing with Redis queue

## Sysntem Architecture

```
┌───────-──┐
│ CLI Tool │
└────────-─┘
     ▼
┌─────────────---------┐   ┌───────-------─┐   ┌────────---------──┐
│ API Server (FastAPI) │ ▶ │ Redis (Queue) │ ◀ │ Worker (Analyzer) │
└─---------────────────┘   └──--───────────┘   └─------────────────┘
     ▲
┌──────────┐
│ Webhooks │
└─────-────┘
```

## Quick Start

### Prerequisites

- Docker and Docker Compose
- OepnAI API key ([Get one here](https://console.openai.com/))
- Anthropic API key ([Get one here](https://console.anthropic.com/))

### Setup

1. **Clone the repository**

```bash
git clone <repo-url>
cd codebase-analyzer
```

2. **Configure environment**

```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY or OPENAI_API_KEY
```

3. **Start the services**

```bash
docker-compose up -d
```

This starts:
- API server on `http://localhost:8000`
- Worker service (background processing)
- Redis (job queue)

## Usage

### Method 1: CLI Tool

The CLI provides the fastest way to analyze codebases:

```bash
# Analyze a codebase
docker-compose run --rm cli analyze /path/to/codebase output-repo-name

# Inspect without creating output
docker-compose run --rm cli inspect /path/to/codebase

# Show version
docker-compose run --rm cli version
```

**Example:**

```bash
docker-compose run --rm cli analyze ./my-project analyzed-project
```

Output:
```
🔍 Analyzing codebase: ./my-project
📦 Output will be created as: analyzed-project

📂 Scanning codebase...
   Found 42 code files

🤖 Analyzing with AI...
   Identified 5 features

📝 Creating Git repository...
   ✓ Master branch initialized

🌿 Creating feature branches...
   ✓ authentication: 3 commits
   ✓ user-management: 5 commits
   ✓ api-endpoints: 4 commits
   ✓ database-layer: 6 commits
   ✓ frontend-ui: 8 commits

🔀 Merging features into master...
   ✓ All features merged

✅ Analysis complete!
📁 Output repository: /app/output/analyzed-project
```

### Method 2: REST API

Perfect for integrating into existing workflows:

**Submit Analysis Job:**

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "repo_path": "/app/workdir/my-project",
    "output_name": "analyzed-project",
    "description": "My awesome project"
  }'
```

Response:
```json
{
  "job_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "queued",
  "message": "Analysis job submitted successfully"
}
```

**Check Job Status:**

```bash
curl http://localhost:8000/status/a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

Response:
```json
{
  "job_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "completed",
  "result": {
    "output_path": "/app/output/analyzed-project",
    "features": [
      {
        "branch": "authentication",
        "feature": "Authentication",
        "commits": 3
      }
    ]
  }
}
```

### Method 3: Webhook

For automated integrations (CI/CD, GitHub Actions, etc.):

```bash
# Generate signature
SECRET="your_webhook_secret"
PAYLOAD='{"repo_path":"/app/workdir/project","output_name":"output"}'
SIGNATURE=$(echo -n "$PAYLOAD" | openssl dgst -sha256 -hmac "$SECRET" | sed 's/^.* //')

# Send webhook
curl -X POST http://localhost:8000/webhook \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Signature: $SIGNATURE" \
  -d "$PAYLOAD"
```

## API Documentation

Once running, visit `http://localhost:8000/docs` for interactive API documentation.

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Service information |
| POST | `/analyze` | Submit analysis job |
| GET | `/status/{job_id}` | Get job status |
| POST | `/webhook` | Webhook endpoint |
| GET | `/health` | Health check |

## Output Structure

The analyzer creates a Git repository with the following structure:

```
output-repo-name/
├── README.md                 # Generated project documentation
├── .git/                     # Git repository
│   ├── refs/heads/
│   │   ├── master           # Main branch (all features merged)
│   │   ├── feature-1        # Individual feature branches
│   │   ├── feature-2
│   │   └── ...
└── [source files organized by feature]
```

### Git History Example

```
* Merge feature: Frontend UI
|\
| * Frontend UI: Add responsive navigation
| * Frontend UI: Implement user dashboard
| * Frontend UI: Create login form
|/
* Merge feature: API Endpoints
|\
| * API Endpoints: Add authentication routes
| * API Endpoints: Implement user CRUD
|/
* Initial commit: Project structure
```

## Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `OPEN_API_KEY` | Your OpenAI API key | Yes | - |
| `ANTHROPIC_API_KEY` | Your Anthropic API key | Yes | - |
| `REDIS_URL` | Redis connection URL | No | `redis://redis:6379` |
| `WEBHOOK_SECRET` | Secret for webhook signature verification | No | `default_secret` |

### Volume Mounts

- `./workdir:/app/workdir` - Input codebases
- `./output:/app/output` - Generated repositories

## Development

### Project Structure

```
codebase-analyzer/
├── docker-compose.yml       # Service orchestration
├── .env.example             # Environment template
├── README.md                # This file
├── api/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── main.py              # FastAPI application
├── worker/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── worker.py            # Background processor
└── cli/
    ├── Dockerfile
    ├── requirements.txt
    └── cli.py               # CLI tool
```

### Running Locally

```bash
# Start all services
docker-compose up

# View logs
docker-compose logs -f

# Restart a service
docker-compose restart worker

# Stop all services
docker-compose down
```

### Debugging

```bash
# Execute commands in running container
docker-compose exec api bash
docker-compose exec worker bash

# View Redis queue
docker-compose exec redis redis-cli
> LLEN job_queue
> KEYS job:*
```

## How It Works

1. **Scanning**: Walks the codebase and collects all source files (excludes node_modules, .git, etc.)

2. **AI Analysis**: Sends code to AI API endpoint with a prompt to:
   - Identify project purpose and description
   - Detect main features and functionality
   - Determine technology stack
   - Break down into logical components
   - Plan commit structure for each feature

3. **Repository Creation**: 
   - Initializes new Git repository
   - Creates master branch with README
   - Generates feature branches for each component

4. **Commit Structure**:
   - Each feature branch gets multiple logical commits
   - Commits include relevant files and changes
   - Meaningful commit messages describe changes

5. **Merging**:
   - Features are merged back to master
   - Uses `--no-ff` to preserve branch history
   - Creates a clean, navigable Git history

## Supported Languages

- Python (.py)
- JavaScript (.js)
- TypeScript (.ts, .tsx)
- Java (.java)
- Go (.go)
- Rust (.rs)
- C/C++ (.c, .cpp, .h)
- React (.jsx, .tsx)
- Vue (.vue)
- Ruby (.rb)
- PHP (.php)
- C# (.cs)
- Swift (.swift)
- Kotlin (.kt)

## Limitations

- Large codebases (>100 files) may take longer to process
- Operation will be limited to codebases with combined filesize < 25MB
- AI analysis is limited by LLM's context window
- Binary files are not processed
- Some file types may not be recognized


## Tools in the Market

Below are some tools currently in the market for manipulating Git history, commit/messages & changelogs:

| **Tool** | **Description** |
|----------|-----------------|
| **RetCOM** | An AI documentation tool that rewrites vague commit messages into professional documentation. It takes your repo and transforms commit messages and change logs. |
| **Smart Commit** | A CLI tool (on PyPI) that uses AI to generate more meaningful commit messages given the repo context. |
| **git‑filter‑repo** | A powerful open source tool for rewriting Git repository history (filtering, rewriting, reorganizing). Doesn’t do AI planning or feature re‑segmentation, but handles heavy history manipulation. |
| **git‑cliff** | A tool for automatic changelog generation from Conventional Commits. |
| **Gitmotion from Elite AI Tools** | A visualization tool to visualize Git repo history. Useful for presenting outcomes. |
| **UtilityForDev Git Commit Generator** | A simple tool to help generate conventional commit messages (web utility). |


## Troubleshooting

### API Key Issues

```bash
# Verify API key is set
docker-compose exec api env | grep OPENAI_API_KEY
```
OR
```bash
# Verify API key is set : using anthropic
docker-compose exec api env | grep ANTHROPIC_API_KEY
```

### Worker Not Processing Jobs

```bash
# Check worker logs
docker-compose logs worker

# Verify Redis connection
docker-compose exec worker python -c "import redis; r=redis.from_url('redis://redis:6379'); r.ping()"
```

### Output Not Generated

```bash
# Check permissions on output directory
ls -la ./output

# Verify Git is installed in containers
docker-compose exec worker git --version
```

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

MIT License - feel free to use this in your projects!

## Credits

Built with:
- AI analysis
    - [OpenAI](https://anthropic.com)
    - [Claude AI](https://anthropic.com)
- [FastAPI](https://fastapi.tiangolo.com) - API framework
- [Redis](https://redis.io) - Job queue
- [Docker](https://docker.com) - Containerization
- [Click](https://click.palletsprojects.com) - CLI framework

---

**Made with ❤️ by the Codebase Analyzer Team**