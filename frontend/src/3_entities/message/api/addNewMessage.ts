// entities/message/api/addNewMessage.ts
import { POST } from "@/4_shared/api/client";
import { Message } from "../model/model";

export const sendMessage = async (chatId: number, content: string): Promise<Message> => {
    const { data, error } = await POST('/api/v0/chat/dialogs/{id}/message', {
        params: {
            path: { id: chatId }
        },
        body: {
            content: content,
            stream: false
        }
    });
    
    if (error) throw error;
    return data as Message;
};