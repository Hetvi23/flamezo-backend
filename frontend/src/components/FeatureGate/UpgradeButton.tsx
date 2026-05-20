/**
 * UpgradeButton — retired under the May 2026 single-tier model.
 *
 * Every onboarded restaurant is on the only available tier (GOLD), so there
 * is nothing to upgrade to. The component is kept as an export with the same
 * props signature for backwards compatibility; it renders `null` so any
 * stray call site silently drops the legacy CTA.
 */

interface UpgradeButtonProps {
  size?: 'sm' | 'md' | 'lg';
  variant?: 'primary' | 'secondary';
  className?: string;
}

// eslint-disable-next-line @typescript-eslint/no-unused-vars
export function UpgradeButton(_props: UpgradeButtonProps) {
  return null;
}
