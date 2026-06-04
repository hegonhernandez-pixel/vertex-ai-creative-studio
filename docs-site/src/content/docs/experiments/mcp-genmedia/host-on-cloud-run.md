---
title: "Hosting MCP Servers on Cloud Run"
---

This guide explains how to containerize and host the Go implementations of Model Context Protocol (MCP) servers on Google Cloud Run using the **Streamable HTTP** transport. 

It also covers how to test these servers locally and how to secure and authenticate clients (like Claude Desktop or other AI agents) to your hosted Cloud Run MCP servers.

---

## 1. Why Streamable HTTP on Cloud Run?

Standard MCP servers typically use the `stdio` transport, which communicates via standard input and output. This works well for local execution, but cannot be easily hosted on serverless platforms.

Cloud Run supports hosting MCP servers via the **Streamable HTTP** (or Server-Sent Events - SSE) transport. Under this protocol:
- The MCP client initiates a session and communicates with the server via standard HTTP `POST` requests carrying JSON-RPC payloads.
- The server responds with `Content-Type: text/event-stream` and streams notifications or updates back to the client.
- Cloud Run handles the secure HTTPS endpoints, scaling, and IAM-based access control automatically.

Every Go MCP server in this repository has built-in support for both `stdio` and `http` (Streamable HTTP) transports.

---

## 2. Local Testing of Streamable HTTP

Before deploying to the cloud, you can test the streamable HTTP transport locally.

### Step 1: Build the Server Binary
Navigate to the root directory of the Go workspace (`experiments/mcp-genmedia/mcp-genmedia-go/`) and build the binary for the server you want to test (e.g., `mcp-imagen-go`):

```bash
cd experiments/mcp-genmedia/mcp-genmedia-go/mcp-imagen-go
go build -o mcp-imagen-go
```

### Step 2: Run the Server in HTTP Mode
Run the server by setting the `-transport` (or `-t`) flag to `http` and specifying a port with `-port` (or `-p`):

```bash
export GOOGLE_CLOUD_PROJECT="your-google-cloud-project-id"
./mcp-imagen-go -transport http -port 9090
```

### Step 3: Perform a Handshake
You can test the HTTP server by simulating an initialize handshake using `curl` or a python script.

An MCP Streamable HTTP client first sends an `initialize` request to the server:

```bash
curl -i -X POST http://localhost:9090/ \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
      "protocolVersion": "2024-11-05",
      "capabilities": {},
      "clientInfo": {
        "name": "test-client",
        "version": "1.0.0"
      }
    }
  }'
```

The response will return:
1. Status `200 OK`
2. A header named `Mcp-Session-Id` (e.g. `mcp-session-xxxx-xxxx-...`)
3. A JSON-RPC body declaring the server's capabilities and details.

For subsequent requests, you must pass the `Mcp-Session-Id` header:

```bash
curl -i -X POST http://localhost:9090/ \
  -H "Content-Type: application/json" \
  -H "Mcp-Session-Id: your-session-id-here" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/list",
    "params": {}
  }'
```

---

## 3. Containerizing the Servers

To host a Go MCP server on Cloud Run, we need to package it into a container image. A generic `Dockerfile` is provided at `experiments/mcp-genmedia/mcp-genmedia-go/Dockerfile`. 

This Dockerfile uses multi-stage builds to produce light-weight production images and uses a build argument (`SERVER_NAME`) to specify which MCP server module to compile.

### Dockerfile Details:
- **Build Stage**: Sets up Go environment, copies the shared library `mcp-common`, and compiles the specified server module (e.g., `mcp-imagen-go`).
- **Run Stage**: Uses a minimal Alpine base image, installs `ca-certificates` and `ffmpeg` (required for `mcp-avtool-go`), and starts the compiled server binary with `-transport http`.

---

## 4. Deploying to Cloud Run

To host a Go MCP server on Cloud Run, you can either deploy using a pre-built container image (if available) or build the container image yourself from source code.

### Option A: Deploying from a Pre-built Public Image (Fastest)

If you are using the official container images published by the project maintainers, you can deploy to Cloud Run with a single command. 

> [!NOTE]
> *(Reference)* The project maintainers are establishing a public Artifact Registry repository to distribute official releases of these MCP servers. Once available, you can deploy them directly without compilation.
>
> Example using a public release image (e.g. `mcp-imagen-go`):

```bash
export REGION=us-central1
export SERVER_NAME=mcp-imagen-go

# Deploy the pre-built image directly
gcloud run deploy ${SERVER_NAME} \
  --image=us-docker.pkg.dev/vertex-ai-creative-studio/mcp-servers/${SERVER_NAME}:latest \
  --region=${REGION} \
  --port=8080 \
  --no-allow-unauthenticated
```

---

### Option B: Building and Deploying from Source (Cloud Build)

If you want to make code changes or build the images yourself, you can use **Google Cloud Build** to compile and build the container image directly in the cloud (no local Docker installation required).

#### Step 1: Create a Private Artifact Registry Repository
Create a Docker repository in your own Google Cloud project to store the compiled images:

```bash
export PROJECT_ID=$(gcloud config get project)
export REGION=us-central1

gcloud artifacts repositories create mcp-servers \
  --repository-format=docker \
  --location=${REGION} \
  --description="Repository for hosted MCP servers"
```

#### Step 2: Build the Container Image in the Cloud
Run the following command from the Go workspace root directory (`experiments/mcp-genmedia/mcp-genmedia-go/`) to build the container image using the workspace Dockerfile:

```bash
export PROJECT_ID=$(gcloud config get project)
export REGION=us-central1
export SERVER_NAME=mcp-imagen-go

# Submit the build to Cloud Build
gcloud builds submit . \
  --tag=${REGION}-docker.pkg.dev/${PROJECT_ID}/mcp-servers/${SERVER_NAME}:latest \
  --build-arg SERVER_NAME=${SERVER_NAME}
```

#### Step 3: Deploy the Custom Image to Cloud Run
Deploy the newly built container image to a Cloud Run service:

```bash
gcloud run deploy ${SERVER_NAME} \
  --image=${REGION}-docker.pkg.dev/${PROJECT_ID}/mcp-servers/${SERVER_NAME}:latest \
  --region=${REGION} \
  --port=8080 \
  --no-allow-unauthenticated
```

On startup, Cloud Run automatically assigns a `PORT` environment variable (default: `8080`). The container entrypoint will automatically bind to it.

### Step 4: Configure IAM Permissions
The Cloud Run service runs under a default service account (or you can create a custom one). Ensure that the service account has the necessary permissions to access Google Cloud services:
1. **Vertex AI User** (`roles/aiplatform.user`): Required for image, video, text, and music generation models.
2. **Storage Object Admin** (`roles/storage.objectAdmin`): Required if the server needs to read/write outputs to a Google Cloud Storage bucket.

```bash
# Get the Cloud Run service account
export SERVICE_ACCOUNT=$(gcloud run services describe ${SERVER_NAME} --region=${REGION} --format="value(spec.template.spec.serviceAccountName)")

# Grant Vertex AI User role
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="roles/aiplatform.user"
```

---

## 5. Authenticating and Connecting Local Clients

Because we deployed the Cloud Run service as **unauthenticated disabled** (`--no-allow-unauthenticated`), standard HTTP requests without credentials will be rejected with a `403 Forbidden` error.

The most secure and convenient way to authenticate a local client (like Claude Desktop or another tool) to the private Cloud Run service is to run the **Cloud Run services proxy** on your local machine.

### Step 1: Start the Cloud Run Proxy
Run the proxy command in your terminal. This creates a secure, authenticated local tunnel on port `3000` that automatically forwards requests to the remote Cloud Run service while injecting your `gcloud` credentials:

```bash
gcloud run services proxy ${SERVER_NAME} \
  --region=${REGION} \
  --port=3000
```
Keep this terminal window open.

### Step 2: Configure the MCP Client
Now, you can configure your local MCP client (such as Claude Desktop) to connect to the local proxy URL.

Open your client config file (e.g., `~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "mcp-imagen-cloudrun": {
      "url": "http://localhost:3000/"
    }
  }
}
```

Restart your MCP client. It will connect to `http://localhost:3000/` which forwards securely to your hosted Cloud Run MCP server.
