"use client";
import {
  ClinicalRecTable,
  DocumentOut,
  getClinicalRecSearch,
} from "@/3_entities/clinicalRec";
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
  Heading,
} from "@radix-ui/themes";
import { useEffect, useState } from "react";

export default function ClinicalRecomendation() {
  const [documents, setDocuments] = useState<DocumentOut[]>([]);
  const [search, setSearch] = useState("");

  const fetchDocuments = async () => {
    const data = await getClinicalRec();
    setDocuments(data);
  };

  const fetchSearchDocuments = async () => {
    const data = await getClinicalRecSearch(search);
    setDocuments(data);
    console.log(data);
  };

  const allDocuments = useAsync(fetchDocuments);
  const searchDocuments = useAsync(fetchSearchDocuments);

  useEffect(() => {
    allDocuments.run();
  }, []);

  if (allDocuments.error)
    return (
      <div style={{ color: "var(--red-10)" }}>Error: {allDocuments.error}</div>
    );

  if (searchDocuments.error)
    return (
      <div style={{ color: "var(--red-10)" }}>Error: {allDocuments.error}</div>
    );

  if (allDocuments.loading || searchDocuments.loading)
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
      <Flex
        gap="3"
        justify="between"
        style={{ // Чтобы закрепить поле ввода на странице
          position: "fixed",
          width: "calc(100% - 2rem)",
          maxWidth: "820px",
          left: "50%",
          transform: "translateX(-50%)",
          zIndex: 10,
        }}
      >
        <TextField.Root
          placeholder="Поиск..."
          style={{ backgroundColor: "var(--gray-4)", width: "100%" }}
          variant="soft"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              e.preventDefault();
              searchDocuments.run();
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
            onClick={() => searchDocuments.run()}
            disabled={!search || searchDocuments.loading}
          >
            Найти
          </Button>
        </Box>
      </Flex>

      <Box
        mt="8"
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
