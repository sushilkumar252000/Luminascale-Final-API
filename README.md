# GFPGAN + Real-ESRGAN Free Production API

A high-performance REST API for face restoration and upscaling powered by GFPGAN and Real-ESRGAN. Designed for production deployment with **API key authentication**, rate limiting, health checks, and GPU optimization.

## ⚡ Features

✅ **Face Enhancement** - AI-powered face restoration and upscaling  
✅ **2x & 4x Upscaling** - Multiple scale factors  
✅ **Free Tier with API Key** - 10,000 requests/day with authentication
✅ **Rate Limiting** - Daily quota management with API key  
✅ **GPU Optimized** - CUDA 12.1 support (NVIDIA L40S, A100, RTX series)  
✅ **Production Ready** - Health checks, restart policies, logging  
✅ **Docker Compose** - One-command deployment  
✅ **Redis Caching** - Fast quota lookups  

---

## 📋 Requirements

- **Docker & Docker Compose** (latest)
- **NVIDIA GPU** with CUDA 12.1+ support
- **8GB+ VRAM** (minimum 12GB recommended)
- **20GB free disk** (for model downloads)
- **Linux/Mac/Windows (WSL2)**

---

## 🚀 Quick Start

### 1. Clone or download this repo

```bash
git clone <repo-url>
cd gfpgan-upscaler-api-free
```

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env` if needed (10,000/day is the default):

```env
FREE_DAILY_LIMIT=10000
REDIS_URL=redis://redis:6379/0
USE_REALESRGAN=1
LOG_LEVEL=info
```

### 3. Deploy with Docker Compose

```bash
docker compose up --build
```

**First run takes ~5-10 min** (downloading GFPGAN + Real-ESRGAN models).

API available at: **http://localhost:8000**

---

## 🔐 Free API Key

**API Key Name:** `freeApiluminascalem`

**Secret Key:** `freeApiluminascalem!+|I1,R1u31C_V`

Use this key in the `X-API-Key` header for all requests.

---

## 📡 API Endpoints

### Health Check

```bash
curl http://localhost:8000/health
```

Response:
```json
{"status": "ok", "timestamp": "...", "service": "GFPGAN Free API", "authentication": "X-API-Key required"}
```

### Enhance Image (Free Tier - Requires API Key)

**POST** `/enhance?scale=2`

```bash
curl -X POST "http://localhost:8000/enhance?scale=2" \
  -H "X-API-Key: freeApiluminascalem!+|I1,R1u31C_V" \
  -F "file=@face.jpg" \
  --output enhanced.png
```

**Parameters:**
- `file` (required) - Image file (JPG, PNG, WebP, etc.)
- `scale` (optional) - `2` or `4` (default: `2`)
- `X-API-Key` (header, required) - Your free API key

**Response:**
- Enhanced image (PNG format)
- HTTP 401 if invalid/missing API key
- HTTP 429 if quota exceeded

**Example Response Headers:**
```
X-Quota-Used: 42
X-Quota-Limit: 10000
X-Quota-Reset: 2024-02-05T23:59:59Z
X-Authenticated: true
```

---

## 🔐 Rate Limiting

**Free tier:** 10,000 requests per 24-hour period per API key

- Rate limit is tracked per API key
- Daily quota resets at **00:00 UTC**
- Quota stored in Redis (fast lookups)
- Returns HTTP 429 when exceeded

Check quota in response headers:
```bash
curl -X POST "http://localhost:8000/enhance?scale=2" \
  -H "X-API-Key: freeApiluminascalem!+|I1,R1u31C_V" \
  -F "file=@face.jpg" \
  -i
```

---

## 🐳 Docker Management

### View logs

```bash
docker compose logs -f api
```

### Stop API

```bash
docker compose down
```

### Restart

```bash
docker compose restart api
```

### Clean up (remove volumes)

```bash
docker compose down -v
```

---

## 🔧 Configuration

### Adjust daily limit

Edit `.env`:

```env
FREE_DAILY_LIMIT=20000  # Increase to 20,000/day
```

Restart:
```bash
docker compose restart api
```

### Disable Real-ESRGAN

```env
USE_REALESRGAN=0  # Uses GFPGAN only (faster)
```

### Change log level

```env
LOG_LEVEL=debug  # For debugging
```

---

## 📊 Performance

Typical timings on L40S GPU:

| Image Size | Scale | Time |
|-----------|-------|------|
| 512x512   | 2x    | 1-2s |
| 512x512   | 4x    | 2-3s |
| 1024x1024 | 2x    | 2-3s |
| 1024x1024 | 4x    | 3-4s |

**Throughput:** ~10-15 images/min on single GPU (2 workers)

---

## 🌐 Deployment to Production

### Remote GPU Server (RunPod, Vast.ai, AWS)

1. SSH into server:
```bash
ssh user@server.com
```

2. Clone repo:
```bash
git clone <repo-url> && cd gfpgan-upscaler-api-free
```

3. Configure:
```bash
cp .env.example .env
```

4. Deploy:
```bash
docker compose up -d
```

5. Verify:
```bash
curl http://localhost:8000/health
```

### Nginx Reverse Proxy (Optional)

Create `nginx.conf`:

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_read_timeout 30s;
    }
}
```

Restart Nginx:
```bash
sudo systemctl restart nginx
```

---

## 🧪 Testing

### Python test script

```python
import requests
from pathlib import Path

API_URL = "http://localhost:8000"

# Upload image
with open("face.jpg", "rb") as f:
    response = requests.post(
        f"{API_URL}/enhance?scale=2",
        files={"file": f}
    )

if response.status_code == 200:
    with open("enhanced.png", "wb") as out:
        out.write(response.content)
    print("✅ Enhancement successful")
    print(f"Quota: {response.headers.get('X-Quota-Used')}/{response.headers.get('X-Quota-Limit')}")
else:
    print(f"❌ Error: {response.status_code}")
    print(response.json())
```

### cURL batch test

```bash
for i in {1..5}; do
  echo "Request $i..."
  curl -X POST "http://localhost:8000/enhance?scale=2" \
    -F "file=@test.jpg" \
    --output "output_$i.png" \
    -w "\nStatus: %{http_code}\n\n"
done
```

---

## 🐛 Troubleshooting

### Port 8000 already in use

```bash
docker compose down
docker compose up
```

### Out of GPU memory

- Reduce image size (max 2048x2048)
- Use `scale=2` instead of `scale=4`
- Reduce worker count in Dockerfile

### Redis connection error

```bash
docker compose down -v
docker compose up
```

### Slow performance

Check GPU usage:
```bash
nvidia-smi
```

Verify CUDA is detected:
```bash
docker compose exec api python3 -c "import torch; print(torch.cuda.is_available())"
```

---

## 📈 Monitoring

### Check API status

```bash
curl http://localhost:8000/health
```

### View container stats

```bash
docker stats gfpgan_api_free gfpgan_redis_free
```

### Check disk usage

```bash
du -sh /var/lib/docker/volumes/*
```

---

## 📝 License

MIT License - See LICENSE file

## 🤝 Support

For issues or feature requests, open a GitHub issue.

---

**Ready for production scale!** 🚀
