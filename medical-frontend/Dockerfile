# Use Node.js base image for the frontend
FROM node:18

# Set working directory
WORKDIR /app

# Copy package files and install dependencies
COPY package*.json ./
RUN npm install

# Copy the rest of the frontend code
COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev"]
