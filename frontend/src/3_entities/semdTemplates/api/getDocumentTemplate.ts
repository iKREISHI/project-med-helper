import { GET } from "@/4_shared/api/client";
import { DocumentTemplate } from "../models/model";

export const getDocumentTemplate = async ({
  page,
  page_size,
}: {
  page: number;
  page_size: number;
}) => {
  try {
    const response = await GET("/api/v0/semd-document-templates/", {
      params: {
        query: {
          page: page,
          page_size: page_size,
        },
      },
    });
    return {
      results: response.data?.results as DocumentTemplate[],
      count: response.data?.count,
    };
  } catch (error) {
    console.error("Fetch documents error:", error);
    throw error;
  }
};
