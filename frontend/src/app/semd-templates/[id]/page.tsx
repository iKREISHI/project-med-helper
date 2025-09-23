import { TemplateForm } from "@/3_entities/semdTemplates";

export default async function Page({ params }: { params: { id: string } }) {
  const { id } = await params;
  const templateId = Number(id);
  return <TemplateForm id={templateId} />;
}
