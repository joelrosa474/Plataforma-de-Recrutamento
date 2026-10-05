import path from "path";
import { fileURLToPath } from "url";

/** @type {import('next').NextConfig} */
const dirname = path.dirname(fileURLToPath(import.meta.url));

const nextConfig = {
  turbopack: {
    root: dirname,
  },
};

export default nextConfig;
