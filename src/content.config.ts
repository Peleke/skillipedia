import { defineCollection, z } from "astro:content";

const entries = defineCollection({
  type: "content",
  schema: z.object({
    id: z.string(),
    name: z.string().optional(),
    type: z.enum(["skill", "pattern", "learning"]),
    claim: z.string(),
    confidence: z.number().min(0).max(1),
    domain: z.string(),
    derivation: z.enum(["literal", "derived"]),
    tags: z.array(z.string()).optional(),
    category: z.string(),
    source_concepts: z.array(z.string()),
    provenance: z.record(z.any()),
    metadata: z.record(z.any()).optional(),
    generated_at: z.string(),
  }),
});

export const collections = { entries };
