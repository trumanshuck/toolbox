import { z } from "zod";
import { createCatalog, generateCatalogPrompt } from "@json-render/core";

// Define a minimal catalog with a few components
export const catalog = createCatalog({
  components: {
    Card: {
      description: "A container card with optional title",
      schema: z.object({
        title: z.string().optional().describe("Card title"),
        children: z.array(z.any()).describe("Card content"),
      }),
    },
    Text: {
      description: "A text element for displaying content",
      schema: z.object({
        content: z.string().describe("The text content to display"),
        variant: z
          .enum(["body", "heading", "caption"])
          .optional()
          .describe("Text style variant"),
      }),
    },
    Button: {
      description: "A clickable button that can trigger actions",
      schema: z.object({
        label: z.string().describe("Button label text"),
        action: z.string().optional().describe("Action ID to trigger on click"),
        variant: z
          .enum(["primary", "secondary", "danger"])
          .optional()
          .describe("Button style variant"),
      }),
    },
  },
  actions: {
    navigate: {
      description: "Navigate to a different page or route",
      schema: z.object({
        path: z.string().describe("The path to navigate to"),
      }),
    },
    showAlert: {
      description: "Display an alert message to the user",
      schema: z.object({
        message: z.string().describe("Alert message text"),
        type: z
          .enum(["info", "success", "warning", "error"])
          .optional()
          .describe("Alert type"),
      }),
    },
  },
});

// Generate the system prompt from the catalog
export const systemPrompt = generateCatalogPrompt(catalog);
