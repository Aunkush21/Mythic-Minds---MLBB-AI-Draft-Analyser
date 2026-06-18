import type { components } from "./schema.d.ts";

type Schemas = components["schemas"];

export type HeroSummary = Schemas["HeroSummary"];
export type HeroDetail = Schemas["HeroDetail"];
export type HeroStatsSummary = Schemas["HeroStatsSummary"];
export type SimilarHeroEntry = Schemas["SimilarHeroEntry"];
export type HeroCounterEntry = Schemas["HeroCounterEntry"];

export type ItemSummary = Schemas["ItemSummary"];
export type EmblemSummary = Schemas["EmblemSummary"];
export type BattleSpellSummary = Schemas["BattleSpellSummary"];
export type PatchSummary = Schemas["PatchSummary"];

export type LanePicks = Schemas["LanePicks"];

export type WinPredictionRequest = Schemas["WinPredictionRequest"];
export type WinPredictionResponse = Schemas["WinPredictionResponse"];

export type HeroPickRequest = Schemas["HeroPickRequest"];
export type HeroPickResponse = Schemas["HeroPickResponse"];
export type HeroPickMeta = Schemas["HeroPickMeta"];
export type BestPickEntry = Schemas["BestPickEntry"];
export type CounterPickEntry = Schemas["CounterPickEntry"];
export type SynergyPickEntry = Schemas["SynergyPickEntry"];

export type BuildRequest = Schemas["BuildRequest"];
export type BuildResponse = Schemas["BuildResponse"];
export type ThreatProfile = Schemas["ThreatProfile"];

export type ExplanationSchema = Schemas["ExplanationSchema"];
export type ExplanationFactorSchema = Schemas["ExplanationFactorSchema"];
export type ConfidenceSchema = Schemas["ConfidenceSchema"];
