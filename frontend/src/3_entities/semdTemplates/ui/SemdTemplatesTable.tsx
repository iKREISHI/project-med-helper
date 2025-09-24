import { Table } from "@radix-ui/themes";
import { DocumentTemplate } from "../models/model";
import styles from "./SemdTemplatesTable.module.css";
import Link from "next/link";

export const SemdTemplatesTable = ({
  documents,
}: {
  documents: DocumentTemplate[];
}) => {
  return (
    <Table.Root variant="ghost" className={styles.Table}>
      <Table.Header>
        <Table.Row>
          <Table.ColumnHeaderCell>№</Table.ColumnHeaderCell>
          <Table.ColumnHeaderCell>Название шаблона</Table.ColumnHeaderCell>
          <Table.ColumnHeaderCell className={styles.HideOnMobile}>
            Описание
          </Table.ColumnHeaderCell>
        </Table.Row>
      </Table.Header>

      <Table.Body>
        {documents.map((file) => (
          <Table.Row key={file.id}>
            <Table.Cell>{file.id}</Table.Cell>
            <Table.Cell className={styles.Truncate}>
              <Link
                className={styles.Title}
                title={file.name}
                href={`/semd-templates/${file.id}`}
              >
                {file.name || "-"}
              </Link>
            </Table.Cell>

            <Table.Cell className={styles.HideOnMobile}>
              {file.description}
            </Table.Cell>
          </Table.Row>
        ))}
      </Table.Body>
    </Table.Root>
  );
};
