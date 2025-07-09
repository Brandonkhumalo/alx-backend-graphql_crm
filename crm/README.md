# CRM Celery Setup Instructions

## 1. Install Redis and Dependencies

Install Redis:
- On Ubuntu: `sudo apt install redis`
- On Docker: `docker run -p 6379:6379 redis`

Install Python dependencies:
```bash
pip install -r requirements.txt