"use client";

import { useRouter } from 'next/navigation';
import { DialogCreate } from '@/3_entities/dialogs/model/model';
import { createDialog } from '@/3_entities/dialogs/api/createDialog';

export function useCreateDialog() {
  const router = useRouter();

  const createNewDialog = async (params: DialogCreate): Promise<void> => {
    try {
      const newDialog = await createDialog(params);
      router.push(`/chat-bot/${newDialog.id}`);
    } catch (error) {
      console.error('Ошибка создания диалога:', error);
      throw error;
    }
  };

  return { createNewDialog };
}