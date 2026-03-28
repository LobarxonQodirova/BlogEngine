# BlogEngine - Advanced Blogging Platform

A production-grade blogging platform with rich text editing, multi-author support, SEO optimization, newsletter management, threaded comments, content scheduling, and full-text search.

## Tech Stack

- **Backend:** Django 5.x + Django REST Framework
- **Frontend:** Next.js 14 (App Router)
- **Database:** PostgreSQL 16
- **Cache/Broker:** Redis 7
- **Task Queue:** Celery 5
- **Search:** Elasticsearch 8
- **Reverse Proxy:** Nginx
- **Containerization:** Docker + Docker Compose

## Features

- Rich text editor with Markdown and WYSIWYG support
- Multi-author blogging with author profiles and dashboards
- Categories, tags, and post series/collections
- SEO optimization with meta tags, Open Graph, and structured data
- Reading time estimation and reading progress indicator
- Newsletter subscription and campaign management
- Threaded comments with voting
- Content scheduling and auto-publishing via Celery
- Media library with folder organization
- Post analytics (views, read time, engagement)
- Full-text search via Elasticsearch
- Responsive design with Tailwind CSS

## Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for local frontend development)
- Python 3.12+ (for local backend development)

## Quick Start

1. Clone the repository:
   ```bash
   git clone https://github.com/your-org/blogengine.git
   cd blogengine
   ```

2. Copy environment variables:
   ```bash
   cp .env.example .env
   ```

3. Edit `.env` with your configuration (database credentials, secret key, etc.)

4. Build and start all services:
   ```bash
   docker-compose up --build
   ```

5. Run database migrations:
   ```bash
   docker-compose exec backend python manage.py migrate
   ```

6. Create a superuser:
   ```bash
   docker-compose exec backend python manage.py createsuperuser
   ```

7. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000/api/
   - Admin Panel: http://localhost:8000/admin/
   - API Docs: http://localhost:8000/api/docs/

## Project Structure

```
blogengine/
├── backend/
│   ├── config/                 # Django project settings
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   ├── asgi.py
│   │   └── celery.py
│   ├── apps/
│   │   ├── accounts/           # User and author management
│   │   ├── posts/              # Blog posts, categories, tags, series
│   │   ├── comments/           # Threaded comments with voting
│   │   ├── newsletter/         # Newsletter subscriptions and campaigns
│   │   ├── media/              # Media file management
│   │   └── analytics/          # Post view tracking and analytics
│   ├── utils/                  # Shared utilities
│   ├── requirements.txt
│   ├── Dockerfile
│   └── manage.py
├── frontend/
│   ├── src/
│   │   ├── app/                # Next.js App Router pages
│   │   ├── components/         # React components
│   │   ├── lib/                # Utility libraries
│   │   ├── context/            # React contexts
│   │   ├── hooks/              # Custom hooks
│   │   └── styles/             # Global styles
│   ├── package.json
│   ├── next.config.js
│   └── Dockerfile
├── nginx/
│   └── nginx.conf
├── docker-compose.yml
├── .env.example
└── .gitignore
```

## API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - JWT login
- `POST /api/auth/token/refresh/` - Refresh JWT token
- `GET /api/auth/profile/` - Get user profile

### Posts
- `GET /api/posts/` - List published posts
- `POST /api/posts/` - Create a post (authenticated)
- `GET /api/posts/{slug}/` - Get post by slug
- `PUT /api/posts/{slug}/` - Update post
- `DELETE /api/posts/{slug}/` - Delete post
- `GET /api/posts/search/` - Full-text search

### Categories & Tags
- `GET /api/categories/` - List categories
- `GET /api/tags/` - List tags

### Series
- `GET /api/series/` - List post series
- `GET /api/series/{slug}/` - Get series with posts

### Comments
- `GET /api/posts/{slug}/comments/` - List comments for a post
- `POST /api/posts/{slug}/comments/` - Add a comment
- `POST /api/comments/{id}/reply/` - Reply to a comment
- `POST /api/comments/{id}/vote/` - Vote on a comment

### Newsletter
- `POST /api/newsletter/subscribe/` - Subscribe to newsletter
- `POST /api/newsletter/unsubscribe/` - Unsubscribe
- `GET /api/newsletter/campaigns/` - List campaigns (admin)
- `POST /api/newsletter/campaigns/send/` - Send campaign (admin)

### Analytics
- `GET /api/analytics/posts/{slug}/` - Post analytics (author)
- `GET /api/analytics/dashboard/` - Dashboard analytics (author)

### Media
- `GET /api/media/` - List media files
- `POST /api/media/upload/` - Upload media file
- `DELETE /api/media/{id}/` - Delete media file

## Development

### Backend (local)
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Frontend (local)
```bash
cd frontend
npm install
npm run dev
```

### Running Tests
```bash
# Backend
docker-compose exec backend python manage.py test

# Frontend
docker-compose exec frontend npm test
```

## Environment Variables

See `.env.example` for all configurable environment variables.

## License

MIT License
