import type { NetworkProvider, ProPlan } from "./types";

export const FREE_MESSAGE_LIMIT = 8;

export const PRO_PLANS: ProPlan[] = [
  { id: "day", label: "1 Day", durationLabel: "24 hours", priceTsh: 620, days: 1 },
  { id: "week", label: "1 Week", durationLabel: "7 days", priceTsh: 3500, days: 7 },
  { id: "month", label: "1 Month", durationLabel: "30 days", priceTsh: 5000, days: 30 },
  { id: "year", label: "1 Year", durationLabel: "365 days", priceTsh: 45000, days: 365 },
];

export function formatTsh(amount: number): string {
  return `TSh ${amount.toLocaleString("en-TZ")}`;
}

export function detectNetwork(phone: string): NetworkProvider {
  const digits = phone.replace(/\D/g, "");
  const local = digits.startsWith("255") ? digits.slice(3) : digits.replace(/^0/, "");
  const prefix = local.slice(0, 2);
  if (["74", "75", "76"].includes(prefix)) return "vodacom";
  if (["71", "65", "67"].includes(prefix)) return "tigo";
  if (["68", "69", "78"].includes(prefix)) return "airtel";
  if (["62", "61"].includes(prefix)) return "halotel";
  return "unknown";
}

export const NETWORK_LABEL: Record<NetworkProvider, string> = {
  vodacom: "M-Pesa (Vodacom)",
  tigo: "Tigo Pesa",
  airtel: "Airtel Money",
  halotel: "HaloPesa",
  unknown: "Mobile money",
};
