"use client";
import { DashboardContainer } from "@/4_shared";
import { DotsHorizontalIcon } from "@radix-ui/react-icons";
import {
  Box,
  DropdownMenu,
  Flex,
  Link,
  Separator,
  Text,
} from "@radix-ui/themes";
import styles from "./files.module.css";
import { fileTypeIcons } from "./fileTypeIcons";
import { useRouter } from "next/navigation";

interface FileItemProps {
  name: string;
  path: string;
  create_at: string;
  type: string;
}

interface FileItemsListProps {
  files?: FileItemProps[];
}

export const FileItemsList = ({ files }: FileItemsListProps) => {
  return (
    <DashboardContainer>
      <Flex align="center" justify="between" pb="5">
        <Box pl="2">
          <Flex gap="3" align="center" wrap={{ initial: "wrap", sm: "nowrap" }}>
            <Text
              size="3"
              style={{
                wordBreak: "break-word",
                minWidth: 0,
                fontWeight: "500",
              }}
            >
              Часто используемые
            </Text>
            {files?.length && (
              <>
                <Box display={{ initial: "none", sm: "block" }}>
                  <Separator orientation="vertical" />
                </Box>
                <Box display={{ initial: "none", sm: "block" }}>
                  <Text size="2" color="gray">
                    {files.length}{" "}
                    {files.length === 1
                      ? "файл"
                      : files.length < 5
                      ? "файла"
                      : "файлов"}
                  </Text>
                </Box>
              </>
            )}
          </Flex>
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

      <Flex direction="column" gap="1" height="100%">
        {files ? (
          files?.map((file, index) => (
            <div key={index}>
              <FileItem
                name={file.name}
                path={file.path}
                create_at={file.create_at}
                type={file.type}
              />
            </div>
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

const FileItem = ({ name, path, create_at, type }: FileItemProps) => {
  const icon = fileTypeIcons[type.toLowerCase()] || fileTypeIcons.default;
  const router = useRouter();
  return (
    <Box
      style={{
        boxShadow: "none",
        padding: "var(--space-2)",
        cursor: "pointer",
      }}
      onClick={() => {
        router.push(path);
      }}
      className={styles.DashboardContainerItem}
    >
      <Flex width="100%" gap="3" align="start">
        <Box className={styles.IconsFiles}>
          <img src={`icons/${icon.icon}`} alt="" />
        </Box>

        <Box style={{ flex: 1, minWidth: 0 }}>
          <Text
            size="3"
            style={{
              overflow: "hidden",
              textOverflow: "ellipsis",
              whiteSpace: "nowrap",
              display: "block",
              width: "100%",
              fontWeight: "500",
            }}
            title={name}
          >
            {name}
          </Text>
          <Flex align="center" justify="between" gap="3" width="100%">
            <Link
              href={path}
              size="2"
              color="gray"
              style={{
                overflow: "hidden",
                textOverflow: "ellipsis",
                whiteSpace: "nowrap",
                maxWidth: "250px",
                flexShrink: 1,
                display: "block",
              }}
              title={path}
            >
              {path}
            </Link>
            <Text size="1" color="gray">
              {create_at}
            </Text>
          </Flex>
        </Box>
      </Flex>
    </Box>
  );
};
