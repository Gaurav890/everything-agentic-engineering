export type ExperienceArchetype = "portfolio" | "product" | "agentic-product";

export type ExperienceManifest = {
  schema_version: number;
  name: string;
  archetype: ExperienceArchetype;
  audience: string;
  promise: string;
  visual_character: "precise" | "bold" | "warm" | "experimental";
  content_status: string;
  preview_all_archetypes?: boolean;
};

export const previewExperiences: Record<ExperienceArchetype, ExperienceManifest> = {
  portfolio: {
    schema_version: 1,
    name: "Mara Voss",
    archetype: "portfolio",
    audience: "ambitious teams looking for a distinctive creative partner",
    promise: "Mara turns complex product challenges into experiences people remember.",
    visual_character: "precise",
    content_status: "reference_fixture",
    preview_all_archetypes: true,
  },
  product: {
    schema_version: 1,
    name: "Northstar",
    archetype: "product",
    audience: "product teams choosing what deserves attention next",
    promise: "Turn competing signals into one decision everyone can act on.",
    visual_character: "precise",
    content_status: "reference_fixture",
    preview_all_archetypes: true,
  },
  "agentic-product": {
    schema_version: 1,
    name: "Relay",
    archetype: "agentic-product",
    audience: "operations teams delegating consequential work",
    promise: "Give agents room to work without giving up human control.",
    visual_character: "bold",
    content_status: "reference_fixture",
    preview_all_archetypes: true,
  },
};
