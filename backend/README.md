# Flask API Backend

A secure Flask REST API backend with user authentication, data storage, and credential management.

## Features

- **User Authentication**: Registration and login with JWT tokens
- **Data Storage**: Store and manage user data items
- **Credential Management**: Store and manage user credentials (passwords, API keys)
- **JSON File Storage**: All data is stored in JSON files in the `data/` directory
- **Secure**: Password hashing, JWT authentication, CORS enabled
- **RESTful API**: Clean REST endpoints for all operations

## Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

Or use a virtual environment (recommended):

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and update the values:

```bash
cp .env.example .env
```

Edit `.env` and set your secret keys:
- `SECRET_KEY`: Flask secret key
- `JWT_SECRET_KEY`: JWT token signing key

**Note**: Data is stored in JSON files in the `data/` directory. The files are automatically created when you first run the application.

### 3. Run the Application

```bash
python app.py
```

The API will be available at `http://localhost:5000`

## API Endpoints

### Authentication

- `POST /api/auth/register` - Register a new user
  ```json
  {
    "username": "user123",
    "password": "password123"
  }
  ```

- `POST /api/auth/login` - Login user
  ```json
  {
    "username": "user123",
    "password": "password123"
  }
  ```

- `GET /api/auth/me` - Get current user (requires JWT token)

### Data Storage

- `GET /api/data` - Get all data items (requires JWT token)
- `POST /api/data` - Create a new data item (requires JWT token)
  ```json
  {
    "title": "My Note",
    "content": "Note content here",
    "data_type": "note",
    "metadata": {"key": "value"}
  }
  ```
- `GET /api/data/<id>` - Get a specific data item (requires JWT token)
- `PUT /api/data/<id>` - Update a data item (requires JWT token)
- `DELETE /api/data/<id>` - Delete a data item (requires JWT token)

### Credential Management

- `GET /api/credentials` - Get all credentials (requires JWT token)
- `POST /api/credentials` - Create a new credential (requires JWT token)
  ```json
  {
    "service_name": "GitHub",
    "username": "myuser",
    "email": "user@example.com",
    "password": "secret123",
    "api_key": "api_key_here",
    "notes": "Personal account"
  }
  ```
- `GET /api/credentials/<id>` - Get a specific credential (requires JWT token)
- `PUT /api/credentials/<id>` - Update a credential (requires JWT token)
- `DELETE /api/credentials/<id>` - Delete a credential (requires JWT token)

### Health Check

- `GET /api/health` - Check API health status

## Using the API

### Authentication Flow

1. Register a new user:
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"test123"}'
```

2. Login to get a JWT token:
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"test123"}'
```

3. Use the token in subsequent requests:
```bash
curl -X GET http://localhost:5000/api/data \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Data Storage

The application uses JSON file storage. All data is stored in the `data/` directory:
- `data/users.json` - User accounts and authentication data
- `data/data_items.json` - User data items
- `data/credentials.json` - User credentials

These files are automatically created when you first run the application. You can view and edit them directly if needed.

## Security Notes

⚠️ **Important**: This is a development setup. For production:

1. Use strong, randomly generated secret keys
2. Enable HTTPS
3. Implement proper encryption for stored credentials (currently stored as plain text)
4. Add rate limiting
5. Implement proper input validation and sanitization
6. Use environment variables for all sensitive configuration
7. Consider using a more secure credential storage solution (e.g., encrypted fields)

## Project Structure

```
backend/
├── app.py              # Main Flask application
├── storage.py          # JSON file storage system
├── models.py           # Data models (legacy, not used)
├── config.py           # Configuration
├── requirements.txt    # Python dependencies
├── data/               # JSON data files (auto-created)
│   ├── users.json
│   ├── data_items.json
│   └── credentials.json
├── .env.example        # Example environment variables
├── .gitignore          # Git ignore file
└── README.md           # This file
```
