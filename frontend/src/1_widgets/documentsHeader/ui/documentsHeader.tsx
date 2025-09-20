"use client";
import { Flex, Select, TextField } from "@radix-ui/themes";
import styles from "./documentsHeader.module.css";
import { MagnifyingGlassIcon } from "@radix-ui/react-icons";
import React, { useState } from "react";

interface FilterProps {
  type: string;
  value: string;
  label: string;
}

export const DocumentsHeader = () => {
  return (
    <Flex align="center" direction="column" gap="3">
      <Flex
        justify="between"
        gap="3"
        width="100%"
        direction={{ initial: "column", lg: "row" }}
      >
        <TextField.Root
          placeholder="Поиск..."
          style={{ backgroundColor: "var(--gray-4)" }}
          variant="soft"
          className={styles.SearchInput}
        >
          <TextField.Slot>
            <MagnifyingGlassIcon height="20" width="20" color="gray" />
          </TextField.Slot>
        </TextField.Root>

        <Flex gap="2" align="center" wrap="wrap">
          <Select.Root size="2" defaultValue="all">
            <Select.Trigger
              placeholder="Тип документа"
              style={{ backgroundColor: "transparent" }}
            />
            <Select.Content className={styles.SelectContent}>
              <Select.Item value="all">Все типы</Select.Item>
              <Select.Item value="contract">Договора</Select.Item>
              <Select.Item value="invoice">Счета</Select.Item>
            </Select.Content>
          </Select.Root>

          <Select.Root size="2" defaultValue="newest">
            <Select.Trigger
              placeholder="Сортировка"
              style={{ backgroundColor: "transparent" }}
            />
            <Select.Content className={styles.SelectContent}>
              <Select.Item value="newest">Сначала новые</Select.Item>
              <Select.Item value="oldest">Сначала старые</Select.Item>
              <Select.Item value="name">По названию</Select.Item>
            </Select.Content>
          </Select.Root>
        </Flex>
      </Flex>
    </Flex>
  );
};
