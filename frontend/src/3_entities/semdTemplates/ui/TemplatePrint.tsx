import { Box, Button } from "@radix-ui/themes";
import { DocumentFieldValueCreate, DocumentTemplate } from "../models/model";

export const TemplatePrint = ({
  document,
  fieldValues,
}: {
  document: DocumentTemplate;
  fieldValues: DocumentFieldValueCreate[];
}) => {
  const getFieldValue = (fieldId: number): string => {
    const val = fieldValues.find((v) => v.field_id === fieldId)?.value;
    return val ? String(val) : "";
  };

  const generateDocxHtml = () => {
    const htmlContent = `
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8" />
    <title>${document.name}</title>
  
  <style>
    body {
        font-family: "Times New Roman", serif;
        font-size: 12pt;
        margin: 2cm 8cm;
        line-height: 1.5;
      }
      .document-title {
        text-align: center;
        text-transform: uppercase;
        font-size: 14pt;
        margin-bottom: 2rem;
      }
      .field-row {
        display: grid;
        grid-template-columns: max-content 1fr;
        gap: 2rem;
        margin-bottom: 0rem;
        padding-bottom: 0.5rem;
      }
      .field-label {
        align-self: center;
      }
      .field-value {
        display: inline-block;
        border-bottom: 1px solid black;
        padding-bottom: 2px;
        min-width: 0;
      }
      .signature-section {
        display: flex;
        justify-content: space-between;
        margin-top: 3rem;
      }
      .document-number {
        display: flex;
        justify-content: space-between;
        margin: 1em 0;
      }

      @media print {
        body {
            margin: 1cm .6cm;
            padding: 0;
            -webkit-print-color-adjust: exact;
        }
}
  </style>
</head>
<body>
  <div class="document-title">${document.name}</div>
  
  <div class="document-number">
    <div>${new Date().toLocaleDateString("ru-RU")}</div>
    <div>№ _________</div>
  </div>

    ${document.fields
      .map(
        ({ field }) => `
    <div class="field-row">
      <div class="field-label">${field.label}</div>
      <div class="field-value">${getFieldValue(field.id) || "&nbsp;"}</div>
    </div>`
      )
      .join("")}
  
  <div class="signature-section">
    <div></div>
    <div>Подпись: _________________________</div>
  </div>
</body>
</html>`;

    return htmlContent;
  };

  const printDocument = () => {
    const htmlContent = generateDocxHtml();
    const printWindow = window.open("", "_blank");
    if (printWindow) {
      printWindow.document.write(htmlContent);
      printWindow.document.close();
    }
  };

  return (
    <Box>
      <Button onClick={printDocument} variant="soft" type="button">
        Просмотр документа
      </Button>
    </Box>
  );
};
