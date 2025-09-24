'use client'

import { Flex } from "@radix-ui/themes";
import styles from './layout.module.css';
import SidebarDialogs, { type LinkItem } from "@/4_shared/ui/sidebarDialogs/sidebarDialogs";
import { useDialogs } from "@/2_features/dialog/useDialogs";
import { useMemo } from "react";

export default function ChatLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const params = useMemo(() => ({ page: 1, page_size: 10 }), []); 

  // Важно: использовать params, а не создавать новый объект здесь
  const { data, loading, error } = useDialogs(params);

  const items: LinkItem[] = (() => {
    if (loading) return [{ id: "loading", title: "Загрузка...", href: "#" }];
    if (error) return [{ id: "error", title: `Ошибка: ${error.message}`, href: "#" }];
    return data?.results?.map((d) => ({
      id: String(d.id),
      title: d.title ?? `Диалог ${d.id}`,
      href: `/chat-bot/${d.id}`,
    })) ?? [];
  })();

  return (
    <Flex direction="row" className={styles.ChatLayout}>
      <SidebarDialogs items={items} />
      <div className={styles.MessagesArea}>
        {children}
      </div>
    </Flex>
  );
}
