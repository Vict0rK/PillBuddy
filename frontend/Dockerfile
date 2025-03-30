# Use Node.js as the base image
FROM node:20

# Set the working directory
WORKDIR /app

# Copy package.json and install dependencies
COPY package.json package-lock.json ./
RUN npm install --legacy-peer-deps

# Copy the entire frontend code
COPY . .

# Build the React app
RUN npm install --force

# Expose the frontend port
EXPOSE 3000

# Start the frontend server
CMD ["npm", "start", "--", "--host", "0.0.0.0"]
