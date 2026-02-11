# Frontend Docker Setup

This frontend is containerized using Docker with nginx serving the built files on port 3002.

## Building the Docker Image

```bash
docker build -t bingo-frontend .
```

## Running the Container

### Using Docker directly:
```bash
docker run -d -p 3002:3002 --name bingo-frontend bingo-frontend
```

### Using Docker Compose:
```bash
docker-compose up -d
```

## Accessing the Application

Once running, the frontend will be available at:
- http://localhost:3002

## Stopping the Container

### Docker:
```bash
docker stop bingo-frontend
docker rm bingo-frontend
```

### Docker Compose:
```bash
docker-compose down
```

## Rebuilding After Changes

If you make changes to the frontend code:

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
docker logs bingo-frontend
```

Or with docker-compose:
```bash
docker-compose logs -f frontend
```

## Notes

- The nginx configuration includes API proxying to `http://backend:5000` if you're using docker-compose with a backend service named "backend"
- For production, you may want to update the API URL in the frontend code or use environment variables
- The build process creates an optimized production build of the React app
