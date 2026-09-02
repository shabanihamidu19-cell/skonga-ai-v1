import type { ChatThread, Entitlement, UserSettings } from "./types";
import { FREE_MESSAGE_LIMIT } from "./plans";

export const defaultSettings = (): UserSettings => ({
  preferredName: "",
  theme: "auto",
  responseStyle: "balanced",
  saveHistory: true,
});

export const defaultEntitlement = (): Entitlement => ({
  isPro: false,
  planId: null,
  expiresAt: null,
});

export function countUserMessages(threads: ChatThread[]): number {
  return threads.reduce(
    (n, t) => n + t.messages.filter((m) => m.role === "user").length,
    0
  );
}

export function remainingFreeMessages(threads: ChatThread[], isPro: boolean): number {
  if (isPro) return Number.POSITIVE_INFINITY;
  return Math.max(0, FREE_MESSAGE_LIMIT - countUserMessages(threads));
}

export function greeting(name: string): string {
  const hour = new Date().getHours();
  const part = hour < 12 ? "Good morning" : hour < 17 ? "Good afternoon" : "Good evening";
  return name.trim() ? `${part}, ${name.trim()}.` : `${part}.`;
}

export function newId(prefix = "id"): string {
  return `${prefix}_${Math.random().toString(36).slice(2, 10)}${Date.now().toString(36)}`;
}
