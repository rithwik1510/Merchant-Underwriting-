import { formatDistanceToNow, format } from "date-fns";

export function formatCurrency(amount: number | null | undefined): string {
  if (amount == null) return "-";
  if (amount >= 1_00_00_000) return `Rs ${(amount / 1_00_00_000).toFixed(1)}Cr`;
  if (amount >= 1_00_000) return `Rs ${(amount / 1_00_000).toFixed(1)}L`;
  if (amount >= 1_000) return `Rs ${(amount / 1_000).toFixed(1)}K`;
  return `Rs ${amount.toLocaleString("en-IN")}`;
}

export function formatPercent(
  value: number | null | undefined,
  decimals = 1
): string {
  if (value == null) return "-";
  return `${(value * 100).toFixed(decimals)}%`;
}

export function formatPercentRaw(
  value: number | null | undefined,
  decimals = 1
): string {
  if (value == null) return "-";
  return `${value.toFixed(decimals)}%`;
}

export function formatNumber(value: number | null | undefined): string {
  if (value == null) return "-";
  if (value >= 1_00_000) return `${(value / 1_00_000).toFixed(1)}L`;
  if (value >= 1_000) return `${(value / 1_000).toFixed(1)}K`;
  return value.toLocaleString("en-IN");
}

export function formatRelativeTime(isoString: string): string {
  try {
    return formatDistanceToNow(new Date(isoString), { addSuffix: true });
  } catch {
    return isoString;
  }
}

export function formatDate(isoString: string): string {
  try {
    return format(new Date(isoString), "dd MMM yyyy, HH:mm");
  } catch {
    return isoString;
  }
}

export function formatMonthLabel(isoMonth: string): string {
  try {
    const [year, month] = isoMonth.split("-");
    const date = new Date(Number(year), Number(month) - 1, 1);
    return format(date, "MMM yy");
  } catch {
    return isoMonth;
  }
}

export function scoreToColor(score: number | null | undefined): string {
  if (score == null) return "#64748B";
  if (score >= 75) return "#2563EB";
  if (score >= 55) return "#1D4ED8";
  if (score >= 40) return "#7C3AED";
  return "#DC2626";
}

export function scoreToBgColor(score: number | null | undefined): string {
  if (score == null) return "rgba(100,116,139,0.12)";
  if (score >= 75) return "rgba(37,99,235,0.12)";
  if (score >= 55) return "rgba(29,78,216,0.12)";
  if (score >= 40) return "rgba(124,58,237,0.12)";
  return "rgba(220,38,38,0.12)";
}
