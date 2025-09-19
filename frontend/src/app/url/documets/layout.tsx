import { Container } from "@radix-ui/themes";
import styles from "./layout.module.css";
import { DocumentsHeader } from "@/1_widgets/documentsHeader";

export default function DocumentsLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <Container py="4" p={{ initial: "4", lg: "0" }}>
      <DocumentsHeader />
      <div className={styles.MessagesArea}>{children}</div>
    </Container>
  );
}
