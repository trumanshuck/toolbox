import { createServer, IncomingMessage, ServerResponse } from "node:http";
import { systemPrompt } from "./catalog.js";

const PORT = 3456;

async function readBody(req: IncomingMessage): Promise<string> {
  const chunks: Buffer[] = [];
  for await (const chunk of req) {
    chunks.push(chunk as Buffer);
  }
  return Buffer.concat(chunks).toString("utf-8");
}

async function handleRequest(
  req: IncomingMessage,
  res: ServerResponse
): Promise<void> {
  // Set CORS headers
  res.setHeader("Content-Type", "application/json");

  if (req.method === "POST" && req.url === "/generate") {
    try {
      const body = await readBody(req);
      const { prompt: userPrompt } = JSON.parse(body || "{}");

      res.writeHead(200);
      res.end(
        JSON.stringify(
          {
            systemPrompt,
            userPrompt: userPrompt || "(no prompt provided)",
          },
          null,
          2
        )
      );
    } catch (error) {
      res.writeHead(400);
      res.end(JSON.stringify({ error: "Invalid JSON body" }));
    }
  } else {
    res.writeHead(404);
    res.end(JSON.stringify({ error: "Not found. Use POST /generate" }));
  }
}

const server = createServer(handleRequest);

server.listen(PORT, () => {
  console.log(`Echo server running at http://localhost:${PORT}`);
  console.log(`\nTest with:`);
  console.log(
    `  curl -X POST http://localhost:${PORT}/generate -d '{"prompt":"Show me a dashboard"}'`
  );
});
