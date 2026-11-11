import type { PartialDate } from "./types";
export function formatDate(date: PartialDate | null | undefined): string {
  if (!date) return "";
  if (date.precision === "year") return date.value;
  const [year, month] = date.value.split("-").map(Number);
  return new Intl.DateTimeFormat("en", {
    month: "short",
    year: "numeric",
    timeZone: "UTC",
  }).format(new Date(Date.UTC(year, month - 1, 1)));
}
export function dateRange(
  start: PartialDate,
  end: PartialDate | null,
  isCurrent: boolean,
) {
  return `${formatDate(start)} — ${isCurrent ? "Present" : formatDate(end)}`;
}
