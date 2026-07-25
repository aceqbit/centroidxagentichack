import { defineNitroConfig } from 'nitropack/config'

export default defineNitroConfig({
  srcDir: 'src',
  routesDir: 'src/routes',
  port: 3002,
  runtimeConfig: {
    databaseUrl: process.env.DATABASE_URL || '',
    redisUrl: process.env.REDIS_URL || '',
    anthropicApiKey: process.env.ANTHROPIC_API_KEY || '',
  },
  typescript: {
    strict: true,
  },
})
