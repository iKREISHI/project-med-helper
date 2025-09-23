import { Badge, Link, Table } from "@radix-ui/themes";
import { DocumentOut } from "../models/model";
import styles from "./ClinicalRecTable.module.css";

export const ClinicalRecTable = ({
  documents,
}: {
  documents: DocumentOut[];
}) => {
  return (
    <Table.Root variant="ghost" className={styles.Table}>
      <Table.Header>
        <Table.Row>
          <Table.ColumnHeaderCell>№</Table.ColumnHeaderCell>
          <Table.ColumnHeaderCell>Название файла</Table.ColumnHeaderCell>
          <Table.ColumnHeaderCell>Статус</Table.ColumnHeaderCell>
          <Table.ColumnHeaderCell className={styles.HideOnMobile}>
            Язык
          </Table.ColumnHeaderCell>
          <Table.ColumnHeaderCell className={styles.HideOnMobile}>
            Источник
          </Table.ColumnHeaderCell>

          <Table.ColumnHeaderCell className={styles.HideOnMobile}>
            Дата создание
          </Table.ColumnHeaderCell>
        </Table.Row>
      </Table.Header>

      <Table.Body>
        {documents.map((file) => (
          <Table.Row key={file.id}>
            <Table.Cell>{file.id}</Table.Cell>
            <Table.Cell className={styles.Truncate}>
              <Link
                size="2"
                onClick={() =>
                  window.open(file.file, "_blank", "noopener,noreferrer")
                }
                className={styles.Title}
                title={file.title}
              >
                {file.title || "-"}
              </Link>
            </Table.Cell>

            <Table.Cell>
              <Badge
                color={
                  file.status?.toLowerCase() === "uploaded"
                    ? "green"
                    : file.status?.toLowerCase() === "parsed"
                    ? "orange"
                    : file.status?.toLowerCase() === "indexed"
                    ? "blue"
                    : file.status?.toLowerCase() === "field"
                    ? "red"
                    : "gray"
                }
              >
                {file.status?.toLowerCase()}
              </Badge>
            </Table.Cell>
            <Table.Cell className={styles.HideOnMobile}>
              {file.language}
            </Table.Cell>
            <Table.Cell className={styles.HideOnMobile}>
              {file.source}
            </Table.Cell>
            <Table.Cell className={styles.HideOnMobile}>
              {new Date(file.created_at).toLocaleString("ru-RU", {
                day: "numeric",
                month: "long",
                year: "numeric",
                hour: "2-digit",
                minute: "2-digit",
              })}
            </Table.Cell>
          </Table.Row>
        ))}
      </Table.Body>
    </Table.Root>
  );
};
