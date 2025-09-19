'use client'

import { Flex } from "@radix-ui/themes";
import styles from './layout.module.css';

export default function ChatLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <Flex direction="column" className={styles.ChatLayout}>
      
      <div className={styles.MessagesArea}>
        {children}
      </div>
    </Flex>
  );
}
