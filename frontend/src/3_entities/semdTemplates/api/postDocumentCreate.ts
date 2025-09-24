import { POST } from "@/4_shared/api/client";
import { DocumentInstance, DocumentInstanceCreate } from "../models/model";

export const postDocumentCreate = async (params: DocumentInstanceCreate) => {
  try {
    const response = await POST("/api/v0/semd-documents/", {
      body: params,
    });

    return response.data as DocumentInstance;
  } catch (error) {
    console.error("Fetch documents error:", error);
    throw error;
  }
};
