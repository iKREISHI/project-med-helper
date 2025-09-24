"use client";
import React, { useEffect, useState } from "react";
import {
  Flex,
  Button,
  DataList,
  Container,
  TextField,
  Heading,
  Text,
  Spinner,
  Callout,
  Badge,
  TextArea,
} from "@radix-ui/themes";
import { DocumentFieldValueCreate, DocumentTemplate } from "../models/model";
import { getDocumentTemplateId } from "../api/getDocumentTemplateId";
import { DashboardContainer, useAsync } from "@/4_shared";
import { postDocumentCreate } from "../api/postDocumentCreate";
import { ArrowLeftIcon, InfoCircledIcon } from "@radix-ui/react-icons";
import { TemplatePrint } from "./TemplatePrint";
import styles from "./SemdTemplatesTable.module.css";
import { useRouter } from "next/navigation";

export const TemplateForm = ({ id }: { id: number }) => {
  const [template, setTemplate] = useState<DocumentTemplate | null>(null);
  const [fieldValues, setFieldValues] = useState<DocumentFieldValueCreate[]>(
    []
  );
  const router = useRouter();

  useEffect(() => {
    if (template) {
      setFieldValues(
        template.fields.map(({ field }) => ({
          field_id: field.id,
          value: "",
        }))
      );
    }
  }, [template]);

  useEffect(() => {
    run();
  }, []);

  const handleChange = (field_id: number, newValue: string) => {
    setFieldValues((currentValues) =>
      currentValues.map((item) =>
        item.field_id === field_id ? { ...item, value: newValue } : item
      )
    );
  };

  const handleSubmti = (e: React.FormEvent) => {
    e.preventDefault();
    console.log(fieldValues);
    createDocument.run();
  };

  const fetchDocumentTemplate = async () => {
    const data = await getDocumentTemplateId(id);
    setTemplate(data);
    console.log(data);
  };

  const fetchDocumentCreate = async () => {
    await postDocumentCreate({ fields: fieldValues, template_id: id });
  };

  const { loading, run, error } = useAsync(fetchDocumentTemplate);
  const createDocument = useAsync(fetchDocumentCreate);

  if (createDocument.error) return <p>{createDocument.error}</p>;

  if (loading)
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

  if (error) return <p>{error}</p>;
  if (!template)
    return (
      <Flex
        style={{
          width: "100%",
          height: "90vh",
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          fontStyle: "italic",
        }}
      >
        Шаблон не найден
      </Flex>
    );

  return (
    <Container size="3" mt="3" m="2">
      <Flex
        onClick={() => router.back()}
        align="center"
        gap="2"
        style={{ cursor: "pointer" }}
        mb="2"
      >
        <ArrowLeftIcon /> Назад
      </Flex>
      <DashboardContainer style={{ padding: "1.5em" }}>
        {createDocument.success && (
          <Callout.Root mb="4">
            <Callout.Icon>
              <InfoCircledIcon />
            </Callout.Icon>
            <Callout.Text>Данные успешно сохранены!</Callout.Text>{" "}
          </Callout.Root>
        )}
        <Flex direction="column" gap="3" mb="7">
          <Flex align="center" gap="3">
            <Badge variant="outline" className={styles.HideOnMobile}>
              Шаблон
            </Badge>
            <Heading weight="bold">{template?.name}</Heading>
          </Flex>
          <Text color="gray" size="2">
            {template?.description}
          </Text>
        </Flex>
        <form action="" onSubmit={handleSubmti}>
          <DataList.Root
            orientation={{ initial: "vertical", lg: "horizontal" }}
          >
            {template.fields.map(({ field }) => {
              const currentValue =
                fieldValues.find((v) => v.field_id === field.id)?.value || "";

              return (
                <DataList.Item key={field.id}>
                  <DataList.Label>
                    {field.label}
                    {field.required && (
                      <span style={{ color: "brown" }}>*</span>
                    )}
                  </DataList.Label>
                  <DataList.Value>
                    {field.field_type == "long_text" ? (
                      <TextArea
                        name={field.key}
                        required={field.required}
                        style={{ flex: 1, backgroundColor: "transparent" }}
                        value={String(currentValue || "")}
                        onChange={(e) => handleChange(field.id, e.target.value)}
                        resize="vertical"
                      />
                    ) : (
                      <TextField.Root
                        type={field.field_type}
                        name={field.key}
                        required={field.required}
                        style={{ flex: 1, backgroundColor: "transparent" }}
                        value={String(currentValue || "")}
                        onChange={(e) => handleChange(field.id, e.target.value)}
                      />
                    )}
                    {/* <TextField.Root
                      type={field.field_type}
                      name={field.key}
                      required={field.required}
                      style={{ flex: 1, backgroundColor: "transparent" }}
                      value={currentValue}
                      onChange={(e) => handleChange(field.id, e.target.value)}
                    /> */}
                  </DataList.Value>
                </DataList.Item>
              );
            })}
          </DataList.Root>
          <Flex gap="3" mt="6">
            <TemplatePrint document={template} fieldValues={fieldValues} />

            <Button size="2" type="submit">
              Сохранить
            </Button>
          </Flex>
        </form>
      </DashboardContainer>
    </Container>
  );
};
