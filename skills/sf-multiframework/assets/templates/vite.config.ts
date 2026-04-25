import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { uiBundle } from "@salesforce/vite-plugin-ui-bundle";
import path from "node:path";

// Minimal Vite config for a Salesforce Multi-Framework UI bundle.
// The @salesforce/vite-plugin-ui-bundle integration proxies Salesforce
// API calls during dev so @salesforce/sdk-data works against a real org.

export default defineConfig({
  plugins: [react(), uiBundle()],
  resolve: {
    alias: {
      "@":           path.resolve(__dirname, "src"),
      "@api":        path.resolve(__dirname, "src/api"),
      "@components": path.resolve(__dirname, "src/components"),
      "@utils":      path.resolve(__dirname, "src/utils"),
      "@styles":     path.resolve(__dirname, "src/styles"),
      "@assets":     path.resolve(__dirname, "src/assets")
    }
  },
  build: {
    outDir: "dist",
    sourcemap: false
  }
});
