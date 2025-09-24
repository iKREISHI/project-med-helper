import { GET } from "@/4_shared/api/client";
import { DocumentOut } from "../models/model";

export const getClinicalRec = async (
  search?: string
): Promise<DocumentOut[]> => {
  try {
    const response = await GET("/api/v0/clinical-recomendation/document/", {
      params: {
        query: {
          search: search,
        },
      },
    });

    return response.data as DocumentOut[];
  } catch (error) {
    console.error("Fetch clinical recomendation error:", error);
    throw error;
  }
};
