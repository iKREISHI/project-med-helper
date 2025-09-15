import { Sidebar } from "@/4_shared";
import styles from "./layout.module.css";

export default function Layout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <div className={styles.Container}>
      <Sidebar
        items={[
          {
            id: "intro",
            title: "Введение",
          },
          {
            id: "chapter1",
            title: "Глава 1: Текс",
            children: [
              { id: "chapter1-1", title: "Текст" },
              {
                id: "chapter1-2",
                title: "Второй текст",
                children: [
                  {
                    id: "chapter1-2-1",
                    title: "Очень длинный текст",
                  },
                ],
              },
            ],
          },
          {
            id: "conclusion",
            title: "Заключение",
          },
        ]}
      />
      <main className={styles.mainContent}>{children}</main>
    </div>
  );
}
