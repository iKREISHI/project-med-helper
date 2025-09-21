import { AuthResponse, LoginModel } from "@/3_entities/auth";
import { POST } from "@/4_shared/api/client";

export const login = async (params: LoginModel): Promise<AuthResponse> => {
  try {
    const response = await POST("/api/v0/auth/login/", {
      body: params,
    });

    if (!response || !response.data) {
      throw new Error("Error: the server returned an empty response.");
    }

    console.log("Response from the server:", response.data);
    return response.data as AuthResponse;
  } catch (error: any) {
    console.error("Authorization error:", error);
    throw new Error(error.message);
  }
};
