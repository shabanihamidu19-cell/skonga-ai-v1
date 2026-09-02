import { useMemo, useState } from "react";
import {
  SafeAreaView,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from "react-native";
import { StatusBar } from "expo-status-bar";
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

export default function App() {
  const [settings, setSettings] = useState(defaultSettings);
  const [entitlement, setEntitlement] = useState(defaultEntitlement);
  const [threads, setThreads] = useState<ChatThread[]>([]);
  const [activeId, setActiveId] = useState<string | null>(null);
  const [draft, setDraft] = useState("");
  const [sheet, setSheet] = useState<"chat" | "menu" | "pro" | "settings">("chat");
  const [planId, setPlanId] = useState<PlanId>("month");
  const [phone, setPhone] = useState("");

  const active = threads.find((t) => t.id === activeId) ?? null;
  const left = remainingFreeMessages(threads, entitlement.isPro);
  const network = detectNetwork(phone);
  const welcome = useMemo(
    () => `${greeting(settings.preferredName)} I'm SKONGA AI.`,
    [settings.preferredName]
  );

  function send() {
    const text = draft.trim();
    if (!text) return;
    if (left <= 0) {
      setSheet("pro");
      return;
    }
    let thread = active;
    if (!thread) {
      thread = {
        id: newId("chat"),
        title: text.slice(0, 32),
        messages: [],
        updatedAt: new Date().toISOString(),
      };
      setThreads((prev) => [thread!, ...prev]);
      setActiveId(thread.id);
    }
    const user = createMessage("user", text);
    const assistant = createMessage("assistant", mockAssistantReply(text, settings.responseStyle));
    setDraft("");
    setThreads((prev) =>
      prev.map((t) =>
        t.id === thread!.id
          ? { ...t, messages: [...t.messages, user, assistant], updatedAt: new Date().toISOString() }
          : t
      )
    );
  }

  function unlock() {
    const plan = PRO_PLANS.find((p) => p.id === planId)!;
    const expires = new Date();
    expires.setDate(expires.getDate() + plan.days);
    setEntitlement({ isPro: true, planId, expiresAt: expires.toISOString() });
    setSheet("chat");
  }

  return (
    <SafeAreaView style={styles.root}>
      <StatusBar style="light" />
      <View style={styles.top}>
        <TouchableOpacity onPress={() => setSheet(sheet === "menu" ? "chat" : "menu")}>
          <Text style={styles.menu}>☰</Text>
        </TouchableOpacity>
        <Text style={styles.title}>SKONGA AI</Text>
        <TouchableOpacity onPress={() => setSheet("pro")}>
          <Text style={styles.pro}>{entitlement.isPro ? "PRO" : "Go Pro"}</Text>
        </TouchableOpacity>
      </View>
      {sheet === "menu" && (
        <View style={styles.panel}>
          <TouchableOpacity style={styles.btn} onPress={() => { setActiveId(null); setSheet("chat"); }}>
            <Text style={styles.btnText}>New Chat</Text>
          </TouchableOpacity>
          {threads.map((t) => (
            <TouchableOpacity key={t.id} onPress={() => { setActiveId(t.id); setSheet("chat"); }}>
              <Text style={styles.thread}>{t.title}</Text>
            </TouchableOpacity>
          ))}
          <TouchableOpacity onPress={() => setSheet("settings")}>
            <Text style={styles.thread}>Settings</Text>
          </TouchableOpacity>
        </View>
      )}
      {sheet === "settings" && (
        <View style={styles.panel}>
          <Text style={styles.h}>Preferred name</Text>
          <TextInput style={styles.input} value={settings.preferredName} onChangeText={(preferredName) => setSettings({ ...settings, preferredName })} />
          <TouchableOpacity style={styles.btn} onPress={() => setSheet("chat")}>
            <Text style={styles.btnText}>Done</Text>
          </TouchableOpacity>
        </View>
      )}
      {sheet === "pro" && (
        <ScrollView style={styles.panel}>
          <Text style={styles.h}>SKONGA Pro</Text>
          {PRO_PLANS.map((p) => (
            <TouchableOpacity key={p.id} style={styles.plan} onPress={() => setPlanId(p.id)}>
              <Text style={{ color: planId === p.id ? "#a78bfa" : "#eef1f7" }}>
                {p.label} — {formatTsh(p.priceTsh)}
              </Text>
            </TouchableOpacity>
          ))}
          <TextInput style={styles.input} placeholder="07XXXXXXXX" placeholderTextColor="#9aa3b5" value={phone} onChangeText={setPhone} keyboardType="phone-pad" />
          <Text style={styles.muted}>{NETWORK_LABEL[network]}</Text>
          <Text style={styles.muted}>PIN inawekwa kwenye simu yako, si ndani ya app.</Text>
          <TouchableOpacity style={styles.btn} onPress={unlock}>
            <Text style={styles.btnText}>Send STK (mock)</Text>
          </TouchableOpacity>
        </ScrollView>
      )}
      {sheet === "chat" && (
        <>
          <ScrollView style={styles.messages} contentContainerStyle={{ padding: 16 }}>
            {!active?.messages.length && <Text style={styles.bubble}>{welcome}</Text>}
            {active?.messages.map((m) => (
              <Text key={m.id} style={[styles.bubble, m.role === "user" && styles.user]}>{m.content}</Text>
            ))}
            {!entitlement.isPro && <Text style={styles.muted}>Free left: {left}</Text>}
          </ScrollView>
          <View style={styles.composer}>
            <TextInput style={styles.input} value={draft} onChangeText={setDraft} placeholder="Ask a question…" placeholderTextColor="#9aa3b5" />
            <TouchableOpacity style={styles.btn} onPress={send}>
              <Text style={styles.btnText}>Send</Text>
            </TouchableOpacity>
          </View>
        </>
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: "#0d0f14" },
  top: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderBottomColor: "#2a3040",
    borderBottomWidth: 1,
  },
  title: { color: "#eef1f7", fontWeight: "700", fontSize: 16 },
  menu: { color: "#eef1f7", fontSize: 22 },
  pro: { color: "#a78bfa", fontWeight: "700" },
  messages: { flex: 1 },
  bubble: { color: "#eef1f7", marginBottom: 12, lineHeight: 22 },
  user: { color: "#a78bfa", textAlign: "right" },
  composer: { flexDirection: "row", gap: 8, padding: 12, alignItems: "center" },
  input: {
    flex: 1,
    borderWidth: 1,
    borderColor: "#2a3040",
    borderRadius: 10,
    color: "#eef1f7",
    paddingHorizontal: 12,
    paddingVertical: 10,
    marginVertical: 8,
  },
  btn: { backgroundColor: "#8b5cf6", borderRadius: 10, paddingHorizontal: 14, paddingVertical: 10 },
  btnText: { color: "white", fontWeight: "700" },
  panel: { padding: 16, flex: 1 },
  h: { color: "#eef1f7", fontSize: 20, fontWeight: "700", marginBottom: 12 },
  thread: { color: "#9aa3b5", paddingVertical: 10 },
  plan: { paddingVertical: 10 },
  muted: { color: "#9aa3b5", marginBottom: 8 },
});
