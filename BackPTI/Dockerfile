FROM node:latest
WORKDIR /back
COPY . .
RUN npm install
EXPOSE 8080
ENTRYPOINT ["node", "index.js"]
