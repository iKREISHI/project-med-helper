import styles from "./page.module.css";
import { Bookmarks, FileDetails, FileItemsList } from "@/1_widgets/dashboard";
import { Container, ScrollArea } from "@radix-ui/themes";

export default function Home() {
  return (
    <ScrollArea
      type="auto"
      style={{
        height: "calc(100vh - 60px)",
      }}
    >
      <Container>
        <div className={styles.Container}>
          <FileDetails
            name="Lorem ipsum dolor sit amet consectetur adipisicing"
            info={{
              create_at: "Пн, Апр 23 2025",
              modified_at: "Пн, Апр 23 2025",
              path: "tmp/",
              size: "1Мб",
              type: "PDF",
            }}
            description="Lorem ipsum dolor sit amet consectetur adipisicing elit. Doloremque nisi laboriosam in hic quibusdam, blanditiis illum voluptatum? Laudantium ex in et, nisi beatae adipisci voluptatem eos debitis quia sequi! Sit."
          />
          <FileItemsList
            files={[
              {
                name: "Максимально длинное название, чтобы оно не влезло в блок",
                path: "tmp/",
                create_at: "05.05.2005",
              },
              {
                name: "Название",
                path: "tmp/tmp/tmp/tmp/tmp/tmp/tmp/tmp/tmp/tmp/tmp/tmp/tmp/tmp/tmp/tmp/",
                create_at: "05.05.2005",
              },
              { name: "Название", path: "tmp/", create_at: "05.05.2005" },
              { name: "Название", path: "tmp/", create_at: "05.05.2005" },
              { name: "Название", path: "tmp/", create_at: "05.05.2005" },
              { name: "Название", path: "tmp/", create_at: "05.05.2005" },
            ]}
          />
          <Bookmarks />
        </div>
      </Container>
    </ScrollArea>
  );
}
