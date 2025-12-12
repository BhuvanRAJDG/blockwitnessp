# BlockWitness - Tamper-Proof Evidence Recorder

## Overview
BlockWitness is a full-stack application for recording and verifying evidence using blockchain technology. Users can upload files which are hashed and stored on a blockchain, allowing later verification of file authenticity.

## Project Structure
```
├── backend/           # Flask backend
│   ├── app.py         # Main Flask application with API routes
│   ├── chain_utils.py # Blockchain hashing utilities
│   ├── crypto_utils.py# Cryptographic signing utilities
│   └── keys/          # RSA keys for signing
├── frontend/          # React + Vite frontend
│   ├── src/
│   │   ├── pages/     # Page components (Login, CreateReport, Verify, etc.)
│   │   ├── components/# Reusable UI components
│   │   └── api.js     # API client functions
│   └── vite.config.js # Vite configuration
└── start.sh           # Startup script for both services
```

## Tech Stack
- **Backend**: Flask, SQLAlchemy, PostgreSQL
- **Frontend**: React 19, Vite 7, Tailwind CSS
- **Authentication**: Email/password + Google OAuth
- **Blockchain**: Custom implementation with SHA-256 hashing and Merkle trees

## Key Features
1. **User Authentication**: Email/password signup and login, Google OAuth integration
2. **Evidence Upload**: Upload files that get hashed and stored on the blockchain
3. **File Verification**: Verify if a file exists in the blockchain by matching hashes
4. **Block Explorer**: Browse all blocks and their transactions
5. **Timeline View**: Chronological view of blockchain activity
6. **Certificate Generation**: Download PDF certificates for verified evidence

## API Endpoints
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `GET /api/auth/me` - Get current user
- `GET /api/auth/google` - Initiate Google OAuth
- `POST /api/report` - Create new evidence report (requires auth)
- `POST /api/verify` - Verify a file against blockchain (requires auth)
- `GET /api/explorer` - List all blocks
- `GET /api/block/<idx>` - Get block details
- `GET /api/chain/timeline` - Get blockchain timeline
- `GET /api/chain/verify` - Verify blockchain integrity

## Environment Variables
- `DATABASE_URL` - PostgreSQL connection string
- `GOOGLE_OAUTH_CLIENT_ID` - Google OAuth client ID
- `GOOGLE_OAUTH_CLIENT_SECRET` - Google OAuth client secret

## Recent Changes (December 2025)
- Added complete authentication system with login/signup
- Integrated Google OAuth for social login
- Fixed file upload and verification endpoints
- Updated API responses to match frontend expectations
- Added @login_required protection to sensitive endpoints
- Fixed Timeline and Explorer data format issues

## Running the Application
The application runs via `bash start.sh` which starts:
1. Flask backend on port 8000
2. Vite dev server on port 5000

The frontend proxies API requests to the backend via Vite's proxy configuration.
