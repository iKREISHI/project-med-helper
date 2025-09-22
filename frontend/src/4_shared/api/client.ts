import createClient from "openapi-fetch/dist/index.cjs";
import { apiConfig } from "../config/backend";
import { paths } from "./types";

function getCookie(name: string): string | null {
  const matches = document.cookie.match(
    new RegExp(
      "(?:^|; )" +
        name.replace(/([\.$?*|{}\(\)\[\]\\\/\+^])/g, "\\$1") +
        "=([^;]*)"
    )
  );
  return matches ? decodeURIComponent(matches[1]) : null;
}

const baseClient = createClient<paths>({
  baseUrl: apiConfig.baseUrl,
  credentials: apiConfig.credentials,
  headers: apiConfig.headers,
});

const csrfMiddleware = {
  async onRequest({ request }: { request: Request }) {
    const csrfToken = getCookie("csrftoken");
    if (csrfToken) {
      request.headers.set("X-CSRFToken", csrfToken);
    }
    return request;
  },
};

baseClient.use(csrfMiddleware);

export const GET = baseClient.GET;
export const POST = baseClient.POST;
export const PUT = baseClient.PUT;
export const DELETE = baseClient.DELETE;
