// src/lib/config.ts
export const backendBaseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const apiConfig = {
  baseUrl: backendBaseUrl,
  credentials: 'include' as const,
  headers: {
    'Content-Type': 'application/json',
  },
};