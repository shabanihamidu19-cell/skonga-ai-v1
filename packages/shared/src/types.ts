export type ThemeMode = "dark" | "light" | "auto";
export type ResponseStyle = "balanced" | "concise" | "detailed";
export type NetworkProvider = "vodacom" | "tigo" | "airtel" | "halotel" | "unknown";

export type PlanId = "day" | "week" | "month" | "year";

export interface ProPlan {
  id: PlanId;
  label: string;
  durationLabel: string;
  priceTsh: number;
  days: number;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  createdAt: string;
}

export interface ChatThread {
  id: string;
  title: string;
  messages: ChatMessage[];
  updatedAt: string;
}

export interface UserSettings {
  preferredName: string;
  theme: ThemeMode;
  responseStyle: ResponseStyle;
  saveHistory: boolean;
}

export interface Entitlement {
  isPro: boolean;
  planId: PlanId | null;
  expiresAt: string | null;
}

export interface PaymentDraft {
  planId: PlanId;
  phone: string;
  network: NetworkProvider;
}
