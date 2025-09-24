import { Table } from "@radix-ui/themes";
import styles from "./SemdTemplatesTable.module.css";
import { PatchedDocumentInstance } from "../models/model";
import { DocumentPrint } from "./DocumentPrint";

export const DocumentsTable = ({
  documents,
}: {
  documents: PatchedDocumentInstance[];
}) => {
  return (
    <Table.Root variant="ghost" className={styles.Table}>
      <Table.Header>
        <Table.Row>
          <Table.ColumnHeaderCell>№</Table.ColumnHeaderCell>
          <Table.ColumnHeaderCell>Название документа</Table.ColumnHeaderCell>
          <Table.ColumnHeaderCell className={styles.HideOnMobile}>
            Дата создания
          </Table.ColumnHeaderCell>
          <Table.ColumnHeaderCell className={styles.HideOnMobile}>
            Дата обновления
          </Table.ColumnHeaderCell>
          <Table.ColumnHeaderCell></Table.ColumnHeaderCell>
        </Table.Row>
      </Table.Header>

      <Table.Body>
        {documents.map((file) => {
          return (
            <Table.Row key={file.id}>
              <Table.Cell>{file.id}</Table.Cell>
              <Table.Cell className={styles.Truncate}>
                {file.template?.name || "-"}
              </Table.Cell>
              <Table.Cell className={styles.HideOnMobile}>
                {file.created_at
                  ? new Date(file.created_at).toLocaleString("ru-RU", {
                      day: "numeric",
                      month: "long",
                      year: "numeric",
                      hour: "2-digit",
                      minute: "2-digit",
                    })
                  : "нет данных"}
              </Table.Cell>
              <Table.Cell className={styles.HideOnMobile}>
                {file.updated_at
                  ? new Date(file.updated_at).toLocaleString("ru-RU", {
                      day: "numeric",
                      month: "long",
                      year: "numeric",
                      hour: "2-digit",
                      minute: "2-digit",
                    })
                  : "нет данных"}
              </Table.Cell>
              <Table.Cell>
                <DocumentPrint document={file} />
              </Table.Cell>
            </Table.Row>
          );
        })}
      </Table.Body>
    </Table.Root>
  );
};
