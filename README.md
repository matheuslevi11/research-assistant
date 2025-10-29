# research-assistant
Research assistant that can read your papers and help you gain insight on it, aiding your literature review.


# Run postgres database to store Knowledge content
```docker run -d \
  --name postgres-ai \
  -e POSTGRES_USER=ai \
  -e POSTGRES_PASSWORD=ai \
  -e POSTGRES_DB=ai \
  -p 5532:5432 \
  postgres:latest```