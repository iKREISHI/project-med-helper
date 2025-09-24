import { GET } from "@/4_shared/api/client";
import { PatchedDocumentInstance } from "../models/model";

export const getDocuments = async ({
  page,
  page_size,
}: {
  page: number;
  page_size: number;
}) => {
  try {
    const response = await GET("/api/v0/semd-documents/", {
      params: {
        query: {
          page: page,
          page_size: page_size,
        },
      },
    });
    return {
      results: response.data?.results as PatchedDocumentInstance[],
      count: response.data?.count,
    };
  } catch (error) {
    console.error("Fetch documents error:", error);
    throw error;
  }
};
