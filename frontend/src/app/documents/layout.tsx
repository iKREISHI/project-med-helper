import styles from "./layout.module.css";

export default function Layout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <div className={styles.Container}>
      <main className={styles.mainContent}>{children}</main>
    </div>
  );
}
