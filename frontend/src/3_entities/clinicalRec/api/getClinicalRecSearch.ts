import { GET } from "@/4_shared/api/client";
import { DocumentOut } from "../models/model";

export const getClinicalRecSearch = async (
  search: string
): Promise<DocumentOut[]> => {
  try {
    const response = await GET(`/api/v0/clinical-recomendation/document/`, {
      parameters: {
        query: { search },
      },
    });

    return response.data as DocumentOut[];
  } catch (error) {
    console.error("Fetch documents error:", error);
    throw error;
  }
};
