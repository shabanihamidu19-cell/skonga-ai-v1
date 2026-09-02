import { useMemo, useState } from "react";
import {
  PRO_PLANS,
  NETWORK_LABEL,
  createMessage,
  defaultEntitlement,
  defaultSettings,
  detectNetwork,
  formatTsh,
  greeting,
  mockAssistantReply,
  newId,
  remainingFreeMessages,
  type ChatThread,
  type PlanId,
} from "@skonga/shared";

export function App() {
  const [settings, setSettings] = useState(defaultSettings);
  const [entitlement, setEntitlement] = useState(defaultEntitlement);
  const [threads, setThreads] = useState<ChatThread[]>([]);
  const [activeId, setActiveId] = useState<string | null>(null);
  const [draft, setDraft] = useState("");
  const [sheet, setSheet] = useState<"none" | "pro" | "settings" | "profile">("none");
  const [planId, setPlanId] = useState<PlanId>("month");
  const [phone, setPhone] = useState("");
  const [payStep, setPayStep] = useState<"plan" | "phone" | "confirm" | "sent">("plan");

  const active = threads.find((t) => t.id === activeId) ?? null;
  const left = remainingFreeMessages(threads, entitlement.isPro);
  const network = detectNetwork(phone);
  const theme =
    settings.theme === "auto"
      ? window.matchMedia("(prefers-color-scheme: light)").matches
        ? "light"
        : "dark"
      : settings.theme;

  const welcome = useMemo(
    () => `${greeting(settings.preferredName)} I'm SKONGA AI — how can I help you today?`,
    [settings.preferredName]
  );

  function ensureThread(): ChatThread {
    if (active) return active;
    const thread: ChatThread = {
      id: newId("chat"),
      title: "New chat",
      messages: [],
      updatedAt: new Date().toISOString(),
    };
    setThreads((prev) => [thread, ...prev]);
    setActiveId(thread.id);
    return thread;
  }

  function send() {
    const text = draft.trim();
    if (!text) return;
    if (left <= 0) {
      setSheet("pro");
      return;
    }
    const thread = ensureThread();
    const user = createMessage("user", text);
    const assistant = createMessage("assistant", mockAssistantReply(text, settings.responseStyle));
    setDraft("");
    setThreads((prev) =>
      prev.map((t) =>
        t.id === thread.id
          ? {
              ...t,
              title: t.messages.length ? t.title : text.slice(0, 32),
              messages: [...t.messages, user, assistant],
              updatedAt: new Date().toISOString(),
            }
          : t
      )
    );
  }

  function startNew() {
    setActiveId(null);
    setDraft("");
  }

  function confirmPay() {
    const plan = PRO_PLANS.find((p) => p.id === planId)!;
    const expires = new Date();
    expires.setDate(expires.getDate() + plan.days);
    setEntitlement({ isPro: true, planId, expiresAt: expires.toISOString() });
    setPayStep("sent");
  }

  return (
    <div className="app" data-theme={theme}>
      <aside className="sidebar">
        <div className="brand">SKONGA AI</div>
        <button className="btn" onClick={startNew}>New Chat</button>
        <div className="threads">
          {threads.map((t) => (
            <div key={t.id} className={`thread ${t.id === activeId ? "active" : ""}`} onClick={() => setActiveId(t.id)}>
              {t.title}
            </div>
          ))}
        </div>
        <div className="foot">
          <button className="btn ghost" onClick={() => setSheet("profile")}>Profile</button>
          <button className="btn ghost" onClick={() => setSheet("settings")}>Settings</button>
        </div>
      </aside>
      <main className="main">
        <header className="top">
          <strong>Your SKONGA Assistant</strong>
          <button className="btn" onClick={() => { setSheet("pro"); setPayStep("plan"); }}>
            {entitlement.isPro ? "Pro" : "Go Pro"}
          </button>
        </header>
        <section className="messages">
          {!active?.messages.length && <p className="bubble">{welcome}</p>}
          {active?.messages.map((m) => (
            <p key={m.id} className={`bubble ${m.role}`}>{m.content}</p>
          ))}
          {!entitlement.isPro && (
            <p className="muted">Free messages left: {Number.isFinite(left) ? left : "∞"}</p>
          )}
        </section>
        <form className="composer" onSubmit={(e) => { e.preventDefault(); send(); }}>
          <input value={draft} onChange={(e) => setDraft(e.target.value)} placeholder="Ask a question…" />
          <button className="btn" type="submit">Send</button>
        </form>
      </main>
      {sheet !== "none" && (
        <div className="sheet-backdrop" onClick={() => setSheet("none")}>
          <div className="sheet" onClick={(e) => e.stopPropagation()}>
            {sheet === "settings" && (
              <>
                <h3>Settings</h3>
                <label className="muted">How should SKONGA call you?</label>
                <input value={settings.preferredName} onChange={(e) => setSettings({ ...settings, preferredName: e.target.value })} />
                <p className="muted">Theme</p>
                <select value={settings.theme} onChange={(e) => setSettings({ ...settings, theme: e.target.value as typeof settings.theme })}>
                  <option value="dark">Dark</option>
                  <option value="light">Light</option>
                  <option value="auto">Auto</option>
                </select>
                <p className="muted">Response style</p>
                <select value={settings.responseStyle} onChange={(e) => setSettings({ ...settings, responseStyle: e.target.value as typeof settings.responseStyle })}>
                  <option value="balanced">Balanced</option>
                  <option value="concise">Concise</option>
                  <option value="detailed">Detailed</option>
                </select>
                <p><button className="btn ghost" onClick={() => { setThreads([]); setActiveId(null); }}>Clear history</button></p>
              </>
            )}
            {sheet === "profile" && (
              <>
                <h3>Profile</h3>
                <p className="muted">Email login will connect to Firebase later.</p>
                <input placeholder="Email" />
                <p><button className="btn">Log in</button></p>
              </>
            )}
            {sheet === "pro" && (
              <>
                <h3>SKONGA Pro</h3>
                {payStep === "plan" && (
                  <>
                    <p className="muted">Choose a plan. Extra messages unlock after payment.</p>
                    <div className="plans">
                      {PRO_PLANS.map((p) => (
                        <div key={p.id} className={`plan ${planId === p.id ? "selected" : ""}`} onClick={() => setPlanId(p.id)}>
                          <span>{p.label}<div className="muted">{p.durationLabel}</div></span>
                          <strong>{formatTsh(p.priceTsh)}</strong>
                        </div>
                      ))}
                    </div>
                    <button className="btn" onClick={() => setPayStep("phone")}>Continue</button>
                  </>
                )}
                {payStep === "phone" && (
                  <>
                    <p className="muted">Phone number for STK Push</p>
                    <input value={phone} onChange={(e) => setPhone(e.target.value)} placeholder="07XXXXXXXX" />
                    <p className="muted">{NETWORK_LABEL[network]}</p>
                    <button className="btn" onClick={() => setPayStep("confirm")}>Continue</button>
                  </>
                )}
                {payStep === "confirm" && (
                  <>
                    <p>An STK Push will be sent to {phone}. Enter your mobile-money PIN on your phone — never inside the app.</p>
                    <button className="btn" onClick={confirmPay}>Confirm</button>
                  </>
                )}
                {payStep === "sent" && (
                  <p>Payment UI complete (mock). Pro is unlocked on this device until a real STK API is wired.</p>
                )}
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
