import type { NextConfig } from 'next';

// GitHub Pages serves the project under /KandelLab/ — enable basePath only there.
// Local dev and Vercel deployments run without GITHUB_PAGES and are unaffected.
const isGithubPages = process.env.GITHUB_PAGES === 'true';

const nextConfig: NextConfig = {
  output: isGithubPages ? 'export' : undefined,
  basePath: isGithubPages ? '/KandelLab' : '',
  assetPrefix: isGithubPages ? '/KandelLab/' : undefined,
  images: {
    unoptimized: true,
  },
};

export default nextConfig;
