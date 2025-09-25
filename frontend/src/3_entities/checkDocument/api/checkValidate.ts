import { POST } from "@/4_shared/api/client"
import { DocumentValidationResponse, ValidResult } from "../model/model"

export const checkValidate = async (id: number): Promise<DocumentValidationResponse | null> => {
    try {
        const response = await POST('/api/v0/validate-document/{id}/validate/', {
            params: {
                path: { id: id }
            },
            body: {
                user: id 
            }
        });
        return response.data as DocumentValidationResponse ;
        
    } catch (error) {
        console.error('Validation error:', error);
        return null;
    }
}