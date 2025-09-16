import styles from "./dashboardContainer.module.css";

interface DashboardContainerProps {
  children?: React.ReactNode;
  className?: string;
  style?: React.CSSProperties;
}

export const DashboardContainer = ({
  children,
  className,
  style,
}: DashboardContainerProps) => {
  return (
    <div className={`${styles.Container} ${className}`} style={style}>
      {children}
    </div>
  );
};
