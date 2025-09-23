import { GET } from "@/4_shared/api/client"
import { PaginatedDialogList, PaginatedDialogListParams } from "../model/model"

export const getAllDialogs = async (params: PaginatedDialogListParams):Promise <PaginatedDialogList> => {
    const response = await GET('/api/v0/chat/dialogs', {
        query: params
    });

    return response.data as PaginatedDialogList;
}