"use client";
import { DashboardContainer } from "@/4_shared";
import styles from "./files.module.css";
import { Badge, Box, Flex, Link, Separator, Text } from "@radix-ui/themes";
import { fileTypeIcons } from "./fileTypeIcons";
import { useRouter } from "next/navigation";

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
  const router = useRouter();
  return (
    <DashboardContainer className={styles.backgroundContainer}>
      <Flex direction="column" height="100%" gap="4">
        {/* <Flex gap="3" justify="between" align="center">
          <Box>
            <Flex
              gap="2"
              align="center"
              wrap={{ initial: "wrap", sm: "nowrap" }}
            >
              <Box display={{ initial: "none", sm: "block" }}>
                <Badge variant="outline">Недавнее</Badge>
              </Box>
              <Text
                size="3"
                style={{
                  wordBreak: "break-word",
                  minWidth: 0,
                  fontWeight: "500",
                }}
              >
                Последнее действие
              </Text>
            </Flex>
          </Box>
          <Text size="1" color="gray">
            {info?.modified_at}
          </Text>
        </Flex> */}

        {name && info ? (
          <Flex
            width="100%"
            gap="4"
            align="center"
            height="100%"
            direction="column"
            pt="1"
          >
            <Flex width="100%" gap="4" align="start" height="100%">
              <Box
                className={styles.IconDetails}
                style={{ cursor: "pointer" }}
                onClick={() => {
                  router.push(info.path || "#");
                }}
              >
                <img
                  src={`icons/${
                    fileTypeIcons[info?.type?.toLowerCase() ?? "default"].icon
                  }`}
                  alt=""
                />
              </Box>

              <Box style={{ flex: 1, minWidth: 0 }}>
                <Flex align="center" justify="between" gap="3" width="100%">
                  <Link
                    href={info.path}
                    size="2"
                    style={{
                      overflow: "hidden",
                      textOverflow: "ellipsis",
                      whiteSpace: "nowrap",
                      maxWidth: "250px",
                      flexShrink: 1,
                      display: "block",
                    }}
                    title={info.path}
                  >
                    {info.path}
                  </Link>
                  <Flex align="center" gap="2">
                    <Box display={{ initial: "none", sm: "block" }}>
                      <Badge variant="soft">Недавнее</Badge>
                    </Box>
                    <Box display={{ initial: "none", sm: "block" }}>
                      <Separator orientation="vertical" />
                    </Box>
                    <Text size="1" color="gray">
                      {info?.modified_at}
                    </Text>
                  </Flex>
                </Flex>
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

                <Flex gap="1" py="2">
                  <Badge variant="solid" style={{ padding: ".3em .8em " }}>
                    {info.size}
                  </Badge>
                  <Badge variant="solid" style={{ padding: ".3em .8em " }}>
                    {info.type}
                  </Badge>
                </Flex>
              </Box>
            </Flex>
            <Text color="gray" size="2">
              {description}
            </Text>
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
