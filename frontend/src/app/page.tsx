import styles from "./page.module.css";
import {
  Bookmarks,
  FileDetails,
  FileGroups,
  FileItemsList,
} from "@/1_widgets/dashboard";
import { Box, Container, Grid, ScrollArea } from "@radix-ui/themes";

export default function Home() {
  return (
    <ScrollArea
      type="auto"
      style={{
        height: "calc(100vh - 60px)",
      }}
    >
      <Container>
        <Box className={styles.Container} py="4" px={{ initial: "4", lg: "0" }}>
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
                type: "xsl",
              },
              {
                name: "Название",
                path: "tmp/tmp/tmp/tmp/tmp/tmp/tmp/tmp/tmp/tmp/tmp/tmp/tmp/tmp/tmp/tmp/",
                create_at: "05.05.2005",
                type: "pdf",
              },
              {
                name: "Название",
                path: "tmp/",
                create_at: "05.05.2005",
                type: "pdf",
              },
              {
                name: "Название",
                path: "tmp/",
                create_at: "05.05.2005",
                type: "docx",
              },
              {
                name: "Название",
                path: "tmp/",
                create_at: "05.05.2005",
                type: "xlsx",
              },
              {
                name: "Название",
                path: "tmp/",
                create_at: "05.05.2005",
                type: "text",
              },
            ]}
          />
          <Grid gap="4" columns={{ initial: "1", md: "2" }}>
            <FileGroups
              items={[
                { id: 1, name: "Группа 1", path: "/groups/1" },
                { id: 2, name: "Группа 2", path: "/groups/2" },
                { id: 3, name: "Группа 3", path: "/groups/3" },
                { id: 3, name: "Группа 3", path: "/groups/3" },
              ]}
            />
            <Bookmarks />
          </Grid>
        </Box>
      </Container>
    </ScrollArea>
  );
}
