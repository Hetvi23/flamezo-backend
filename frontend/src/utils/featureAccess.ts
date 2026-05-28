/**
 * Centralized Feature Access Control
 *
 * Under the May 2026 single-tier business model every onboarded restaurant is
 * on GOLD (the only active tier) and therefore has access to every feature on
 * day one. The helper and constants below are retained for backwards
 * compatibility with the many components that import them, but they now
 * always report "unlocked".
 */

export type PlanType = 'GOLD';

export const GOLD_ONLY_FEATURES: string[] = [];

export function getFeatureAccessStatus(_plan: PlanType, _feature?: string) {
  return { isLocked: false, requiredTier: null as PlanType | null };
}
