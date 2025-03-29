# Use LTS Node.js instead of v23 (better stability)
FROM node:20

WORKDIR /app

# Copy package files first for caching
COPY package*.json ./

# Install dependencies (include devDependencies)
RUN npm install

# Copy the rest
COPY . .