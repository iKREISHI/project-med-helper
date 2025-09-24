"use client";
import { useAsync } from "@/4_shared";
import {
  Flex,
  Box,
  Container,
  Spinner,
  Text,
  IconButton,
} from "@radix-ui/themes";
import { useEffect, useState } from "react";
import { ChevronLeftIcon, ChevronRightIcon } from "@radix-ui/react-icons";
import { ITEMS_ON_PAGE } from "@/3_entities/semdTemplates";
import {
  DocumentsTable,
  getDocuments,
  PatchedDocumentInstance,
} from "@/3_entities/documents";

export default function ClinicalRecomendation() {
  const [documents, setDocuments] = useState<PatchedDocumentInstance[]>([]);
  const [totalPages, setTotalPages] = useState<number | undefined>(0);
  const [currentPage, setCurrentPage] = useState(1);

  const fetchDocuments = async (page: number = 1) => {
    const data = await getDocuments({ page, page_size: ITEMS_ON_PAGE });
    setDocuments(data.results || []);
    const totalCount = data.count ?? 0;
    setTotalPages(Math.ceil(totalCount / ITEMS_ON_PAGE));
  };

  const allDocuments = useAsync((page?: number) => fetchDocuments(page));

  useEffect(() => {
    allDocuments.run(currentPage);
  }, [currentPage]);

  const handlePreviousPage = () => {
    if (currentPage > 1) {
      setCurrentPage(currentPage - 1);
    }
  };

  const handleNextPage = () => {
    if (currentPage < (totalPages || 0)) {
      setCurrentPage(currentPage + 1);
    }
  };

  if (allDocuments.error)
    return (
      <div style={{ color: "var(--red-10)" }}>Error: {allDocuments.error}</div>
    );

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
          Список документов
        </Text>
      </Box>
      <Box
        style={{
          backgroundColor: "white",
          borderRadius: "var(--radius-4)",
          boxShadow: "0 1px 6px 0 rgb(0 0 0 / 0.04)",
        }}
        p="3"
      >
        <DocumentsTable documents={documents} />
      </Box>

      {/* Пагинация */}
      <Flex justify="end" align="center" gap="3" p="3">
        <Text size="2" color="gray">
          Страницы: {currentPage} из {totalPages}
        </Text>
        <IconButton
          variant="soft"
          disabled={currentPage === 1}
          onClick={handlePreviousPage}
          size="1"
        >
          <ChevronLeftIcon />
        </IconButton>
        <IconButton
          variant="soft"
          disabled={currentPage === totalPages}
          onClick={handleNextPage}
          size="1"
        >
          <ChevronRightIcon />
        </IconButton>
      </Flex>
    </Container>
  );
}
