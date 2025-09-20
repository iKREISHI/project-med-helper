interface IconConfig {
  icon: string;
}

export const fileTypeIcons: Record<string, IconConfig> = {
  pdf: {
    icon: "PDF.svg",
  },
  docx: {
    icon: "DOCX.svg",
  },
  doc: {
    icon: "DOC.svg",
  },
  txt: {
    icon: "TXT.svg",
  },
  png: {
    icon: "PNG.svg",
  },
  xsl: {
    icon: "XSL.svg",
  },
  default: {
    icon: "DEFAULT.svg",
  },
};
