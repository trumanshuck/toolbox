#!/usr/bin/env bun
import { parse as parseYaml } from "yaml";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import { join } from "node:path";

interface Variation {
  name: string;
  prompt: string;
  references?: string[];
  source?: string;
}

interface Config {
  source: string;
  model?: "pro" | "max" | "klein";
  variations: Variation[];
}

const MODEL_ENDPOINTS = {
  pro: "https://api.bfl.ai/v1/flux-2-pro-preview",
  max: "https://api.bfl.ai/v1/flux-2-max",
  klein: "https://api.bfl.ai/v1/flux-2-klein-preview",
} as const;

async function toBase64(path: string): Promise<string> {
  const buf = await readFile(path);
  return buf.toString("base64");
}

async function submit(
  apiKey: string,
  endpoint: string,
  body: Record<string, unknown>,
): Promise<{ id: string; polling_url: string }> {
  const res = await fetch(endpoint, {
    method: "POST",
    headers: { "x-key": apiKey, "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`submit ${res.status}: ${await res.text()}`);
  return res.json() as Promise<{ id: string; polling_url: string }>;
}

async function poll(
  apiKey: string,
  pollingUrl: string,
  intervalMs = 2000,
  timeoutMs = 15 * 60 * 1000,
): Promise<string> {
  const start = Date.now();
  while (true) {
    if (Date.now() - start > timeoutMs) throw new Error(`poll timeout: ${pollingUrl}`);
    const res = await fetch(pollingUrl, { headers: { "x-key": apiKey } });
    if (!res.ok) throw new Error(`poll ${res.status}: ${await res.text()}`);
    const data = (await res.json()) as { status: string; result?: { sample?: string } };
    if (data.status === "Ready") {
      const url = data.result?.sample;
      if (!url) throw new Error(`Ready but no sample url: ${JSON.stringify(data)}`);
      return url;
    }
    if (["Error", "Failed", "Content Moderated", "Request Moderated"].includes(data.status)) {
      throw new Error(`generation ${data.status}: ${JSON.stringify(data)}`);
    }
    await Bun.sleep(intervalMs);
  }
}

async function download(url: string, dest: string) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`download ${res.status}`);
  await writeFile(dest, Buffer.from(await res.arrayBuffer()));
}

async function runOne(
  apiKey: string,
  endpoint: string,
  variation: Variation,
  defaultSource: string,
  outDir: string,
) {
  const sourcePath = variation.source ?? defaultSource;
  const body: Record<string, unknown> = {
    prompt: variation.prompt,
    input_image: await toBase64(sourcePath),
  };
  const refs = variation.references ?? [];
  for (let i = 0; i < refs.length; i++) {
    body[`input_image_${i + 2}`] = await toBase64(refs[i]);
  }

  console.log(`[${variation.name}] submit`);
  const { polling_url } = await submit(apiKey, endpoint, body);
  console.log(`[${variation.name}] poll`);
  const url = await poll(apiKey, polling_url);
  const dest = join(outDir, `${variation.name}.png`);
  await download(url, dest);
  console.log(`[${variation.name}] saved → ${dest}`);

  await writeFile(
    join(outDir, `${variation.name}.json`),
    JSON.stringify({ ...variation, source: sourcePath, endpoint, result_url: url }, null, 2),
  );
  return dest;
}

async function runAll<T>(items: T[], limit: number, fn: (item: T) => Promise<unknown>) {
  const queue = [...items];
  await Promise.all(
    Array.from({ length: limit }, async () => {
      while (queue.length) {
        const item = queue.shift()!;
        try {
          await fn(item);
        } catch (e) {
          console.error(e);
        }
      }
    }),
  );
}

async function main() {
  const apiKey = process.env.BFL_API_KEY;
  if (!apiKey) {
    console.error("BFL_API_KEY not set. Add it to .env (Bun auto-loads .env).");
    process.exit(1);
  }
  const configPath = process.argv[2] ?? "variations.yaml";
  const concurrency = Number(process.env.CONCURRENCY ?? 3);
  const config = parseYaml(await readFile(configPath, "utf8")) as Config;
  const model = config.model ?? "pro";
  const endpoint = MODEL_ENDPOINTS[model];
  if (!endpoint) throw new Error(`unknown model: ${model}`);

  const stamp = new Date().toISOString().replace(/[:.]/g, "-").replace("T", "_").slice(0, 19);
  const outDir = join("outputs", stamp);
  await mkdir(outDir, { recursive: true });
  console.log(
    `out=${outDir} model=${model} source=${config.source} n=${config.variations.length} concurrency=${concurrency}`,
  );
  await runAll(config.variations, concurrency, (v) =>
    runOne(apiKey, endpoint, v, config.source, outDir),
  );
  console.log("done.");
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
