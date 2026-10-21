# Expects a prebuilt SPA in ./dist (run `npm run build` first).
# Avoids pulling node:* from Docker Hub (rate limits).
# Full in-image build: see Dockerfile.build when Hub is available.
FROM nginx:1.27-alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
