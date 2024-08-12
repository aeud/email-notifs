# Email notifications

## Start the server

```bash
flask --app main run
```

## Send a fake request

```bash
echo '{
    "message": "🎉 this is a message",
    "subject": "🎉 hello you",
    "to": "xxxx@gmail.com",
    "cta_link": "https://www.google.com/"
}' | base64
# ewogICAgIm1lc3NhZ2UiOiAi8J+OiSB0aGlzIGlzIGEgbWVzc2FnZSIsCiAgICAic3ViamVjdCI6ICLwn46JIGhlbGxvIHlvdSIsCiAgICAidG8iOiAieHh4eEBnbWFpbC5jb20iLAogICAgImN0YV9saW5rIjogImh0dHBzOi8vd3d3Lmdvb2dsZS5jb20vIgp9Cg==
curl \
    -XPOST localhost:5000 \
    -H "Content-Type: application/json" \
    -d '{
        "message": {
            "data": "ewogICAgIm1lc3NhZ2UiOiAi8J+OiSB0aGlzIGlzIGEgbWVzc2FnZSIsCiAgICAic3ViamVjdCI6ICLwn46JIGhlbGxvIHlvdSIsCiAgICAidG8iOiAieHh4eEBnbWFpbC5jb20iLAogICAgImN0YV9saW5rIjogImh0dHBzOi8vd3d3Lmdvb2dsZS5jb20vIgp9Cg=="
        }
    }'
```

## Build the image

```bash
gcloud builds submit . \
    --region=REGION \
    --tag us.gcr.io/PROJECT_ID/image/url:tag \
    --project PROJECT_ID
```