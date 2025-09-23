import { GET, POST } from "@/4_shared/api/client"
import { PaginatedDialogList, PaginatedDialogListParams, DialogCreate, Dialog } from "../model/model"

export const createDialog = async (params: DialogCreate):Promise <Dialog> => {
    const response = await POST('/api/v0/chat/dialogs', {
        body: params
    });

    return response.data as Dialog;
}