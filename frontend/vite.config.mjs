import { defineConfig } from "vite";
import { resolve } from "path";
import fs from "fs";

export default defineConfig(({ command }) => {
  const isDev = command === "serve";

  return {
    base: "/static/vite/",

    build: {
      manifest: true,
      outDir: resolve("../static/vite"),
      emptyOutDir: true,
      rollupOptions: {
        input: {
          main: resolve("./src/main.js"),
        },
      },
    },

    server: isDev
      ? {
          host: "0.0.0.0",
          port: 5173,
          https: {
            key: fs.readFileSync("../.mock_certs/key.pem"),
            cert: fs.readFileSync("../.mock_certs/cert.pem"),
          },
          origin: "https://localhost:5173",
          fs: {
            allow: [".."],
          },
        }
      : undefined,

    resolve: {
      alias: {
        "@": resolve("./src"),
      },
    },
  };
});
