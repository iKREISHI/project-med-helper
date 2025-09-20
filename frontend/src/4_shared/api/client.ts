//API-клиент @4_shared/api/client.ts
//Типы генерируются в types.ts

import createClient from "openapi-fetch/dist/index.cjs";
import { apiConfig, backendBaseUrl } from "../config/backend";

export const { GET, POST, PUT, DELETE } = createClient<paths> ({
    baseUrl: apiConfig.baseUrl,
    credentials: apiConfig.credentials,
    headers: apiConfig.headers
}
)