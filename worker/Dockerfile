FROM mcr.microsoft.com/playwright:v1.49.1-noble
WORKDIR /worker
COPY package.json package-lock.json* ./
RUN npm install --omit=dev
COPY audit.mjs ./
USER pwuser
ENTRYPOINT ["node", "audit.mjs"]
