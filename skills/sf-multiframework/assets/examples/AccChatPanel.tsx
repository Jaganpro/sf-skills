/**
 * Agentforce Conversation Client (ACC) — minimal mount.
 *
 * Prerequisites in Setup (see references/acc-integration.md):
 *   - Agentforce preference enabled, Employee Agent configured
 *   - My Domain: "Require first-party use of Salesforce cookies" UNCHECKED
 *   - Session Settings → Trusted Domains for Inline Frames includes this app's
 *     origin (prod, preview, AND http://localhost:<port>) with iFrame type Lightning Out
 *
 * Install:
 *   npm install @salesforce/agentforce-conversation-client
 *
 * NOTE: The exact `createAccWidget` option shape evolves with the package
 *       version. Always check the installed version's TypeScript declarations.
 */

import { useEffect, useRef } from "react";
import { createAccWidget } from "@salesforce/agentforce-conversation-client";

interface Props {
  mode?: "floating" | "docked" | "inline";
}

export function AccChatPanel({ mode = "floating" }: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const widgetRef = useRef<{ destroy: () => void } | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    widgetRef.current = createAccWidget({
      container: containerRef.current,
      mode,
      welcomeMessage: "How can I help today?",
      brand: {
        primaryColor: "#0176d3",
        borderRadius: "0.5rem"
      }
    });

    return () => {
      widgetRef.current?.destroy();
      widgetRef.current = null;
    };
  }, [mode]);

  return <div ref={containerRef} className="acc-host" />;
}
