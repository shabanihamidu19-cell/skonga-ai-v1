import type { ChatMessage, ResponseStyle } from "./types";

export function mockAssistantReply(userText: string, style: ResponseStyle): string {
  const trimmed = userText.trim();
  const base =
    `I'm SKONGA AI, your Tanzanian student assistant. ` +
    `You asked: "${trimmed.slice(0, 180)}${trimmed.length > 180 ? "…" : ""}". ` +
    `This client build uses a local mock until the chat backend is connected.`;

  if (style === "concise") {
    return `Got it. ${base} Next: connect POST /chat.`;
  }
  if (style === "detailed") {
    return `${base}\n\nSuggested next steps:\n1. Point the app at your API.\n2. Wire STK Push for Pro.\n3. Ground answers with the TIE library API.`;
  }
  return base;
}

export function createMessage(role: ChatMessage["role"], content: string): ChatMessage {
  return {
    id: `msg_${Math.random().toString(36).slice(2, 10)}`,
    role,
    content,
    createdAt: new Date().toISOString(),
  };
}
