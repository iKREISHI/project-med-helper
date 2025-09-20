"use client";
import React from "react";
import { DashboardContainer } from "@/4_shared";
import { Box, Flex, Link, Separator, Text } from "@radix-ui/themes";
import { CaretRightIcon, FileIcon } from "@radix-ui/react-icons";
import { useRouter } from "next/navigation";

interface FileGroupProps {
  id: number;
  name: string;
  path: string;
}

interface FileGroupsProps {
  items: FileGroupProps[];
}

export function FileGroups({ items }: FileGroupsProps) {
  const router = useRouter();
  return (
    <DashboardContainer>
      <Flex direction="column" gap="1" justify="between" height="100%">
        <Flex gap="2" direction="column">
          {items.map((group, index) => (
            <Box key={index} p="1">
              <Flex
                width="100%"
                gap="4"
                align="start"
                style={{ cursor: "pointer" }}
                onClick={() => {
                  router.push(group.path);
                }}
              >
                {/* <Box style={{ paddingTop: ".5em" }}>
                  <img src="icons/folder.svg" alt="" width="35px" />
                </Box> */}
                <Box
                  style={{
                    padding: "var(--space-2)",
                    background: "var(--accent-3)",
                    borderRadius: "var(--radius-2)",
                    flexShrink: 0,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                  }}
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="20"
                    height="20"
                    fill="currentColor"
                    viewBox="0 0 16 16"
                    style={{ color: "var(--accent-11)" }}
                  >
                    <path d="M.54 3.87.5 3a2 2 0 0 1 2-2h3.672a2 2 0 0 1 1.414.586l.828.828A2 2 0 0 0 9.828 3h3.982a2 2 0 0 1 1.992 2.181l-.637 7A2 2 0 0 1 13.174 14H2.826a2 2 0 0 1-1.991-1.819l-.637-7a2 2 0 0 1 .342-1.31zM2.19 4a1 1 0 0 0-.996 1.09l.637 7a1 1 0 0 0 .995.91h10.348a1 1 0 0 0 .995-.91l.637-7A1 1 0 0 0 13.81 4zm4.69-1.707A1 1 0 0 0 6.172 2H2.5a1 1 0 0 0-1 .981l.006.139q.323-.119.684-.12h5.396z" />
                  </svg>
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
                  >
                    {group.name}
                  </Text>
                  <Flex align="center" justify="between" gap="3" width="100%">
                    <Link
                      color="gray"
                      href={group.path}
                      size="2"
                      style={{
                        overflow: "hidden",
                        textOverflow: "ellipsis",
                        whiteSpace: "nowrap",
                        maxWidth: "250px",
                        flexShrink: 1,
                        display: "block",
                      }}
                    >
                      {group.path}
                    </Link>
                  </Flex>
                </Box>

                <Box>
                  <CaretRightIcon width="20px" height="20px" color="gray" />
                </Box>
              </Flex>
              {index < items.length - 1 && (
                <Separator
                  size="4"
                  style={{
                    backgroundColor: "var(--gray-4)",
                    margin: ".6em 0",
                  }}
                />
              )}
            </Box>
          ))}
        </Flex>
        <Flex pt="3" justify="end" style={{ cursor: "pointer" }}>
          <Link href="/all-groups">Показать все</Link>
        </Flex>
      </Flex>
    </DashboardContainer>
  );
}
