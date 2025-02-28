# -----------------------------
# 1) Build Stage (Node)
# -----------------------------
    FROM node:18 as build

    WORKDIR /app
    COPY package*.json ./
    
    # Install dependencies
    RUN npm install
    
    # Copy the rest of the application
    COPY . .
    
    # Build React app
    RUN npm run build
    
    # -----------------------------
    # 2) Nginx Stage
    # -----------------------------
    FROM nginx:alpine
    
    # Remove default config if desired
    RUN rm /etc/nginx/conf.d/default.conf
    
    # Copy the build from Node stage
    COPY --from=build /app/build /usr/share/nginx/html
    
    # Copy our custom Nginx config
    COPY default.conf /etc/nginx/conf.d/default.conf
    
    # Expose port 80 in the container
    EXPOSE 80
    
    CMD ["nginx", "-g", "daemon off;"]
    