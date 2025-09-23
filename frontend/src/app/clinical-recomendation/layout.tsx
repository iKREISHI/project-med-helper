"use client";

import { Flex } from "@radix-ui/themes";
import styles from "./layout.module.css";

export default function ClinicalRecLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <Flex direction="column" className={styles.ClinicalRecLayout}>
      <div className={styles.Content}>{children}</div>
    </Flex>
  );
}
