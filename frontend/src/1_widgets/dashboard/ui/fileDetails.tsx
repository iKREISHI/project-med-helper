import { DashboardContainer } from "@/4_shared";
import styles from "./files.module.css";
import {
  Badge,
  Box,
  Button,
  DataList,
  Flex,
  Heading,
  Link,
  Text,
} from "@radix-ui/themes";

interface FileDetailsProps {
  name?: string;
  info?: {
    create_at?: string;
    path?: string;
    size?: string;
    type?: string;
    modified_at?: string;
  };
  description?: string;
}

export const FileDetails = ({ name, info, description }: FileDetailsProps) => {
  return (
    <DashboardContainer className={styles.backgroundContainer}>
      <Flex direction="column" height="100%" gap="4">
        <Box>
          <Badge size="2">Последнее действие</Badge>
        </Box>
        {name && info ? (
          <Flex direction="column" justify="between" height="100%" gap="4">
            <Flex direction="column" gap="4">
              <Heading size="3" weight="bold">
                {name}
              </Heading>

              <DataList.Root>
                <DataList.Item>
                  <DataList.Label>Размер файла</DataList.Label>
                  <DataList.Value>{info.size}</DataList.Value>
                </DataList.Item>

                <DataList.Item>
                  <DataList.Label>Тип</DataList.Label>
                  <DataList.Value>{info.type}</DataList.Value>
                </DataList.Item>

                <DataList.Item>
                  <DataList.Label>Путь</DataList.Label>
                  <DataList.Value>
                    <Link
                      href={info.path}
                      size="2"
                      className={styles.TruncateOneLine}
                    >
                      {info.path}
                    </Link>
                  </DataList.Value>
                </DataList.Item>

                <DataList.Item>
                  <DataList.Label>Дата создания</DataList.Label>
                  <DataList.Value>{info.create_at}</DataList.Value>
                </DataList.Item>

                <DataList.Item>
                  <DataList.Label>Последнее изменение</DataList.Label>
                  <DataList.Value>{info.modified_at}</DataList.Value>
                </DataList.Item>
              </DataList.Root>
              <DataList.Root orientation="vertical">
                <DataList.Item>
                  <DataList.Label>Описание</DataList.Label>
                  <DataList.Value>{description}</DataList.Value>
                </DataList.Item>
              </DataList.Root>
            </Flex>
            <Box>
              <Button variant="surface">Открыть файл</Button>
            </Box>
          </Flex>
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
