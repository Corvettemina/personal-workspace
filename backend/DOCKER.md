# Backend Docker Setup

This backend is containerized using Docker with gunicorn serving the Flask app on port 6000.

## Building the Docker Image

```bash
docker build -t bingo-backend .
```

## Running the Container

### Using Docker directly:
```bash
docker run -d -p 6000:6000 \
  -v $(pwd)/data:/app/data \
  -e SECRET_KEY=your-secret-key \
  -e JWT_SECRET_KEY=your-jwt-secret-key \
  --name bingo-backend \
  bingo-backend
```

### Using Docker Compose:
```bash
docker-compose up -d
```

## Accessing the API

Once running, the backend API will be available at:
- http://localhost:6000/api

## Environment Variables

You can set these environment variables:

- `SECRET_KEY` - Flask secret key (default: dev-secret-key-change-in-production)
- `JWT_SECRET_KEY` - JWT token signing key (default: jwt-secret-key-change-in-production)

Create a `.env` file in the backend directory or set them in docker-compose.yml.

## Data Persistence

The `data/` directory is mounted as a volume, so your JSON data files will persist between container restarts.

## Stopping the Container

### Docker:
```bash
docker stop bingo-backend
docker rm bingo-backend
```

### Docker Compose:
```bash
docker-compose down
```

## Rebuilding After Changes

If you make changes to the backend code:

```bash
# Stop the container
docker-compose down

# Rebuild the image
docker-compose build

# Start again
docker-compose up -d
```

Or in one command:
```bash
docker-compose up -d --build
```

## Viewing Logs

```bash
docker logs bingo-backend
```

Or with docker-compose:
```bash
docker-compose logs -f backend
```

## Gunicorn Configuration

The backend uses gunicorn with the following settings:
- **Workers**: Automatically calculated based on CPU cores (CPU * 2 + 1)
- **Port**: 6000
- **Timeout**: 120 seconds
- **Logging**: Outputs to stdout/stderr

You can modify `gunicorn.conf.py` to adjust these settings.

## Notes

- The data directory is mounted as a volume for data persistence
- Make sure to set strong secret keys in production
- The container runs with gunicorn in production mode
- CORS is enabled to allow frontend connections
