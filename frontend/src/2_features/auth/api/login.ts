import { AuthResponse, LoginModel } from "@/3_entities/auth";
import { POST } from "@/4_shared/api/client";

export const login = async (params: LoginModel): Promise<AuthResponse> => {
  try {
    const result = await POST("/api/v0/auth/login/", {
      body: params,
    });

    const errorData = result.error;
    const response = result.data;
    const status = result.response?.status;

    if (status >= 400) {
      const errorMessage =
        (errorData &&
        typeof errorData === "object" &&
        "non_field_errors" in errorData
          ? (errorData as any).non_field_errors?.[0]
          : null) || `Authentication failed with status: ${status}`;
      throw new Error(errorMessage);
    }

    return response as AuthResponse;
  } catch (error: any) {
    console.error("Authorization error:", error);
    throw error instanceof Error ? error : new Error("Authorization failed");
  }
};
