
### Production Deployment

#### Step 1: Build and Tag Docker Images
On your local machine, build the Docker images:
```bash
# Build frontend image
docker buildx build -t q4-frontend:latest ./frontend

# Build backend image
docker buildx build -t q4-backend:latest ./backend
```

#### Step 2: Save Images as TAR Files
Export the images to portable TAR files:
```bash
# Save frontend image
docker save -o q4-frontend.tar q4-frontend:latest

# Save backend image
docker save -o q4-backend.tar q4-backend:latest
```

#### Step 3: Upload to VPS
Transfer the necessary files to your VPS:
```bash
# Create deployment directory on VPS (if needed)
ssh -P 10241 root@srv17.mikr.us "mkdir -p /root/q4_v2"

# Upload files
scp -P 10241 q4-frontend.tar q4-backend.tar \
    Dockerfile docker-compose.yml \
    .env.production \
    root@srv17.mikr.us:/root/q4_v2
```

#### Step 4: Deploy on VPS
SSH into your VPS and load the images:
```bash
# SSH into the server
ssh -P 10241 root@srv17.mikr.us

# Navigate to project directory
cd /root/q4_v2

# Load Docker images
docker load -i q4-frontend.tar
docker load -i q4-backend.tar

# Start the services
docker compose up -d
```

### Environment Variables

#### Frontend (.env.production)
```env
NEXT_PUBLIC_BACKEND_URL=https://your-backend-url
```

#### Backend (.env)
```env
OPENAI_API_KEY=your_openai_key
ELEVENLABS_API_KEY=your_elevenlabs_key
ALLOWED_ORIGINS=https://your-frontend-domain.com
```

### Maintenance

#### Updating the Application
To update the application with new changes:

1. Build new images locally:
```bash
docker buildx build -t q4-frontend:latest ./frontend
docker buildx build -t q4-backend:latest ./backend
```

2. Save and transfer:
```bash
docker save -o q4-frontend.tar q4-frontend:latest
docker save -o q4-backend.tar q4-backend:latest
scp -P 10296 q4-*.tar root@srv17.mikr.us:/root/q4
```

3. On the VPS:
```bash
cd /root/q4_v2
docker compose down
docker load -i q4-frontend.tar
docker load -i q4-backend.tar
docker compose up -d
```

#### Backup
To backup your data:
```bash
# On the VPS
cd /root/q4
tar -czf q4_backup.tar.gz .env* *.yml *.tar
```

### Troubleshooting

1. If the frontend can't connect to the backend:
   - Check NEXT_PUBLIC_BACKEND_URL in frontend environment
   - Verify ALLOWED_ORIGINS in backend environment
   - Check if the backend service is running

2. If images fail to load:
   - Ensure enough disk space is available
   - Verify file permissions
   - Check if Docker daemon is running

3. For logs:
```bash
# View all logs
docker compose logs

# View specific service logs
docker compose logs frontend
docker compose logs backend
```

## License
[Your License Here] 