"use client";
import { ClinicalRecTable, DocumentOut } from "@/3_entities/clinicalRec";
import { getClinicalRec } from "@/3_entities/clinicalRec";
import { useAsync } from "@/4_shared";
import { MagnifyingGlassIcon } from "@radix-ui/react-icons";
import {
  Flex,
  TextField,
  Button,
  Box,
  Container,
  Spinner,
  Text,
} from "@radix-ui/themes";
import { useEffect, useState } from "react";

export default function ClinicalRecomendation() {
  const [documents, setDocuments] = useState<DocumentOut[]>([]);
  const [search, setSearch] = useState("");

  const fetchDocuments = async () => {
    const data = await getClinicalRec(search);
    setDocuments(data);
  };

  const allDocuments = useAsync(fetchDocuments);

  useEffect(() => {
    allDocuments.run();
  }, []);

  const errorMessage = allDocuments.error;
  if (errorMessage) {
    return <div style={{ color: "var(--red-10)" }}>Error: {errorMessage}</div>;
  }

  if (allDocuments.loading)
    return (
      <Flex
        style={{
          width: "100%",
          height: "90vh",
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
        }}
      >
        <Spinner />
      </Flex>
    );

  return (
    <Container m="4">
      <Box mb="3" ml="1">
        <Text weight="medium" size="3" color="gray">
          Клинические рекомендации
        </Text>
      </Box>
      <Flex gap="3" justify="between">
        <TextField.Root
          placeholder="Поиск..."
          style={{ backgroundColor: "var(--gray-4)", width: "100%" }}
          variant="soft"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              e.preventDefault();
              allDocuments.run();
            }
          }}
        >
          <TextField.Slot>
            <MagnifyingGlassIcon height="20" width="20" color="gray" />
          </TextField.Slot>
        </TextField.Root>
        <Box>
          <Button
            size="2"
            onClick={() => allDocuments.run()}
            disabled={!search || allDocuments.loading}
          >
            Найти
          </Button>
        </Box>
      </Flex>

      <Box
        mt="4"
        style={{
          backgroundColor: "white",
          borderRadius: "var(--radius-4)",
          boxShadow: "0 1px 6px 0 rgb(0 0 0 / 0.04)",
        }}
        p="3"
      >
        <ClinicalRecTable documents={documents} />
      </Box>
    </Container>
  );
}
