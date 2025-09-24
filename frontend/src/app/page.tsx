'use client';
import styles from "./page.module.css";
import {
  Bookmarks,
  FileDetails,
  FileGroups,
  FileItemsList,
} from "@/1_widgets/dashboard";
import { useDocuments } from "@/2_features/mainPage/useDocument";
import { Box, Container, Grid, ScrollArea } from "@radix-ui/themes";
import path from "path";

export default function Home() {
  const {data, last, loading, error} = useDocuments();
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
            name={last?.template?.name}
            info={{
              create_at: last?.created_at,
              modified_at: last?.created_at,
              path: "/semd-templates",
              size: '1mb',
              type: "PDF",
            }}
            description = {'Последний документ'}
          />
          <FileItemsList
  files={data?.map(file => ({
    name: file.template?.name,
    path: '/semd-templates',
    create_at: file.created_at,
    type: 'pdf'
  }))}
/>
          <Grid gap="4" columns={{ initial: "1", md: "2" }}>
<FileGroups
  items={[
    {id:1, name: 'Обследования', path:'/documents'},
    {id:2, name: 'Правовая информация', path:'/documents'},
    {id:3, name: 'Отчетность', path:'/documents'}
  ]}
/>
            <Bookmarks />
          </Grid>
        </Box>
      </Container>
    </ScrollArea>
  );
}
