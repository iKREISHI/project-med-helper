"use client";
import { useCallback, useEffect, useRef, useState } from "react";
import styles from "./sidebar.module.css";

export interface BookItem {
  id: string;
  title: string;
  children?: BookItem[];
}

interface SidebarProps {
  items: BookItem[];
  className?: string;
}

export const Sidebar = ({ className, items }: SidebarProps) => {
  const [isSidebarOpen, setSidebarOpen] = useState(true);
  const [sidebarWidth, setSidebarWidth] = useState(250);
  const sidebarRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleResize() {
      if (window.innerWidth <= 768 && isSidebarOpen) {
        setSidebarOpen(false);
      }
    }
    handleResize();
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  // Изменение размера
  const startResizing = useCallback(
    (e: React.MouseEvent) => {
      e.preventDefault();

      const onMouseMove = (moveEvent: MouseEvent) => {
        const newWidth = sidebarWidth + moveEvent.clientX - e.clientX;
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
      className={`${className} ${styles.Sidebar} ${
        !isSidebarOpen ? styles.closed : ""
      }`}
      style={{ width: isSidebarOpen ? `${sidebarWidth}px` : "0" }}
    >
      <div
        className={styles.ButtonToggle}
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
        <div className={`${styles.ResizeHandle}`} onMouseDown={startResizing} />
      )}

      <div className={styles.SidebarScrollContainer}>
        <div className={styles.SidebarContent}>
          {isSidebarOpen && (
            <>
              {items.map((item) => (
                <SidebarItemProps key={item.id} item={item} />
              ))}
            </>
          )}
        </div>
      </div>
    </aside>
  );
};

interface SidebarItemProps {
  item: BookItem;
  level?: number;
}

const SidebarItemProps = ({ item, level = 0 }: SidebarItemProps) => {
  const [isOpen, setIsOpen] = useState(false);
  const hasChildren = item.children?.length;

  return (
    <div
      style={{ paddingLeft: level * 13 }}
      className={level !== 0 ? styles.SidebarItemBorderLeft : ""}
    >
      <div
        className={styles.SidebarItem}
        onClick={() => hasChildren && setIsOpen((prev) => !prev)}
      >
        {hasChildren && (
          <span className={styles.ButtonToggleItem}>
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="14"
              height="14"
              fill="currentColor"
              className={`${isOpen ? styles.SvgOpen : ""}`}
              viewBox="0 0 16 16"
            >
              <path
                fillRule="evenodd"
                d="M4.646 1.646a.5.5 0 0 1 .708 0l6 6a.5.5 0 0 1 0 .708l-6 6a.5.5 0 0 1-.708-.708L10.293 8 4.646 2.354a.5.5 0 0 1 0-.708"
              />
            </svg>
          </span>
        )}

        <a href={`#${item.id}`} onClick={(e) => e.stopPropagation()}>
          {item.title}
        </a>
      </div>

      {/* Аккордеон */}
      {hasChildren && isOpen && (
        <div>
          {item.children?.map((child) => (
            <SidebarItemProps key={child.id} item={child} level={level + 1} />
          ))}
        </div>
      )}
    </div>
  );
};
