import { DashboardContainer } from "@/4_shared";
import { DotsHorizontalIcon } from "@radix-ui/react-icons";
import { Badge, Box, DropdownMenu, Flex, Link, Text } from "@radix-ui/themes";
import styles from "./files.module.css";

interface FileItemProps {
  name: string;
  path: string;
  create_at: string;
}

interface FileItemsListProps {
  files?: FileItemProps[];
}

export const FileItemsList = ({ files }: FileItemsListProps) => {
  return (
    <DashboardContainer>
      <Flex align="center" justify="between" pb="20px">
        <Box>
          <Badge size="2" color="gray">
            Часто используемые файлы
          </Badge>
        </Box>

        <DropdownMenu.Root>
          <DropdownMenu.Trigger className={styles.DropdownTrigger}>
            <DotsHorizontalIcon width="16px" height="16px" />
          </DropdownMenu.Trigger>
          <DropdownMenu.Content className={styles.DropdownContent}>
            <DropdownMenu.Item className={styles.DropdownItem}>
              Очистить
            </DropdownMenu.Item>
          </DropdownMenu.Content>
        </DropdownMenu.Root>
      </Flex>

      <Flex direction="column" gap="10px" height="100%">
        {files ? (
          files?.map((file, index) => (
            <FileItem
              key={index}
              name={file.name}
              path={file.path}
              create_at={file.create_at}
            />
          ))
        ) : (
          <Flex align="center" justify="center" height="100%">
            <Text style={{ fontStyle: "italic" }} color="gray">
              Пусто
            </Text>
          </Flex>
        )}
      </Flex>
    </DashboardContainer>
  );
};

const FileItem = ({ name, path, create_at }: FileItemProps) => {
  return (
    <DashboardContainer
      style={{ boxShadow: "none", border: "1px solid var(--gray-4)", backgroundColor: 'var(--accent-1)' }}
    >
      <Flex align="center" justify="between" gap="3">
        <Link href={path} size="2" className={styles.TruncateOneLine}>
          {path}
        </Link>
        <Text
          size="1"
          color="gray"
          style={{
            flexShrink: 0,
            whiteSpace: "nowrap",
          }}
        >
          {create_at}
        </Text>
      </Flex>
      <Text
        size="3"
        weight="bold"
        className={styles.TruncateOneLine}
        style={{ display: "block" }}
        title={name}
      >
        {name}
      </Text>
    </DashboardContainer>
  );
};
