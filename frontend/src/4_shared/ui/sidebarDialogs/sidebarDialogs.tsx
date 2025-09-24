// components/Sidebar.tsx
"use client";

import React, { useCallback, useEffect, useRef, useState } from "react";
import styles from "./sidebarDialogs.module.css";
import { Button } from "@radix-ui/themes";
import { createDialog } from "@/3_entities/dialogs/api/createDialog";
import { title } from "process";
import { useCreateDialog } from "@/2_features/dialog/newDialog";

export interface LinkItem {
  id: string;
  title: string;
  href: string;
}

interface SidebarProps {
  items: LinkItem[];
  className?: string;
}

export const SidebarDialogs: React.FC<SidebarProps> = ({ className, items }) => {
  const initialOpen =
    typeof window === "undefined" ? true : window.innerWidth > 768;
  const [isSidebarOpen, setSidebarOpen] = useState<boolean>(initialOpen);
  const [sidebarWidth, setSidebarWidth] = useState<number>(250);
  const sidebarRef = useRef<HTMLDivElement | null>(null);
  const { createNewDialog } = useCreateDialog();

  useEffect(() => {
    function handleResize() {
      if (window.innerWidth <= 768) setSidebarOpen(false);
      else setSidebarOpen(true);
    }
    handleResize();
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  // ресайз боковой панели
  const startResizing = useCallback(
    (e: React.MouseEvent) => {
      e.preventDefault();
      const startX = e.clientX;
      const startWidth = sidebarWidth;

      const onMouseMove = (moveEvent: MouseEvent) => {
        const delta = moveEvent.clientX - startX;
        const newWidth = startWidth + delta;
        if (newWidth >= 200 && newWidth <= 450) {
          setSidebarWidth(newWidth);
        }
      };

      const onMouseUp = () => {
        document.removeEventListener("mousemove", onMouseMove);
        document.removeEventListener("mouseup", onMouseUp);
      };

      document.addEventListener("mousemove", onMouseMove);
      document.addEventListener("mouseup", onMouseUp);
    },
    [sidebarWidth]
  );

  return (
    <aside
      ref={sidebarRef}
      className={`${className ?? ""} ${styles.Sidebar} ${
        !isSidebarOpen ? styles.closed : ""
      }`}
      style={{ width: isSidebarOpen ? `${sidebarWidth}px` : "0" }}
      aria-hidden={!isSidebarOpen}
    >
      <div
        className={styles.ButtonToggle}
        role="button"
        aria-pressed={isSidebarOpen}
        onClick={() => setSidebarOpen((prev) => !prev)}
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="16"
          height="16"
          fill="currentColor"
          className={`${isSidebarOpen ? styles.SvgClosed : ""}`}
          viewBox="0 0 16 16"
        >
          <path
            fillRule="evenodd"
            d="M4.646 1.646a.5.5 0 0 1 .708 0l6 6a.5.5 0 0 1 0 .708l-6 6a.5.5 0 0 1-.708-.708L10.293 8 4.646 2.354a.5.5 0 0 1 0-.708"
          />
        </svg>
      </div>

      {isSidebarOpen && (
        <div
          className={styles.ResizeHandle}
          onMouseDown={startResizing}
          aria-hidden="true"
        />
      )}

      <div className={styles.SidebarScrollContainer}>
        <div className={styles.SidebarContent}>
          {isSidebarOpen &&
            items.map((item) => <SidebarLink key={item.id} item={item}/>)}
        </div>
        
      </div>
     <div className={styles.ButtonContainer}>
  <Button 
    className={styles.Button} 
    onClick={() => createNewDialog({ title: 'Новый чат' })}
  >
    Новый диалог
  </Button>
</div>
    </aside>
  );
};

const SidebarLink: React.FC<{ item: LinkItem }> = ({ item }) => {
  return (
    <div className={styles.SidebarItemWrapper}>
      <a className={styles.SidebarItem} href={item.href}>
        {item.title}
      </a>
    </div>
  );
};

export default SidebarDialogs;
