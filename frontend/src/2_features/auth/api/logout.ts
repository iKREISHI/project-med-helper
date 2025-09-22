import { POST } from "@/4_shared/api/client";

export const logout = async () => {
  try {
    await POST("/api/v0/auth/logout/");
  } catch (error) {
    console.error("Exit error:", error);
  }
};
