import { GET } from "@/4_shared/api/client";
import { DocumentTemplate } from "../models/model";

export const getDocumentTemplateId = async (id: number) => {
  try {
    const response = await GET("/api/v0/semd-document-templates/{id}/", {
      params: {
        path: { id },
      },
    });

    return response.data as DocumentTemplate;
  } catch (error) {
    console.error("Fetch documents error:", error);
    throw error;
  }
};
