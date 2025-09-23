import { GET } from "@/4_shared/api/client";
import { DocumentOut } from "../models/model";

export const getClinicalRec = async (): Promise<DocumentOut[]> => {
  try {
    const response = await GET("/api/v0/clinical-recomendation/document/");
    return response.data as DocumentOut[];
  } catch (error) {
    console.error("Fetch documents error:", error);
    throw error;
  }
};
