import { GET } from "@/4_shared/api/client";
import { User } from "../model/models";

export const getCurrentUser = async (): Promise<User> => {
  const response = await GET("/api/v0/users/me/");

  if (!response.data) {
    throw new Error("No user data received");
  }

  return response.data;
};
