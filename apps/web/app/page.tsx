import {EnterpriseLab} from "./enterprise-lab";
import type {EnterpriseManifest} from "@everything-agentic/types";
import {PortfolioLab} from "./portfolio-lab";
import {ProductLab} from "./product-lab";
import {
  previewExperiences,
  type ExperienceArchetype,
  type ExperienceManifest,
} from "./experience-types";
import designState from "../../../.agentic/design.json";
import enterpriseState from "../../../.agentic/enterprise.json";
import experienceState from "../../../.agentic/experience.json";

export default async function Page({
  searchParams,
}: {
  searchParams: Promise<{archetype?: string; character?: string}>;
}) {
  const query = await searchParams;
  const requested = query.archetype;
  const allowArchetypePreview = experienceState.preview_all_archetypes === true;
  const archetype: ExperienceArchetype =
    allowArchetypePreview &&
    (requested === "product" || requested === "agentic-product" || requested === "portfolio" || requested === "enterprise-workflow")
      ? requested
      : (experienceState.archetype as ExperienceArchetype);
  const requestedCharacter = query.character;
  const visualCharacter =
    allowArchetypePreview &&
    (requestedCharacter === "precise" ||
      requestedCharacter === "bold" ||
      requestedCharacter === "warm" ||
      requestedCharacter === "experimental")
      ? requestedCharacter
      : experienceState.visual_character;
  const baseExperience =
    archetype === experienceState.archetype
      ? experienceState
      : previewExperiences[archetype];
  const experience = {
    ...baseExperience,
    visual_character: visualCharacter,
  } as ExperienceManifest;
  const approvedDirection =
    designState.status === "approved" ? (designState.approved_direction as string | null) : null;

  if (archetype === "enterprise-workflow") {
    return (
      <EnterpriseLab
        experience={experience}
        enterprise={enterpriseState as EnterpriseManifest}
        approvedDirection={approvedDirection}
      />
    );
  }

  if (archetype !== "portfolio") {
    return <ProductLab experience={experience} approvedDirection={approvedDirection} />;
  }

  const profile = {
    name: experience.name,
    role: "Product designer & creative technologist",
    location: "London ↔ anywhere",
  };

  return <PortfolioLab profile={profile} approvedDirection={approvedDirection} />;
}
