"use client";
import * as React from "react";
import { CaretDownIcon, ExitIcon } from "@radix-ui/react-icons";
import styles from "./header.module.css";
import { Box, Flex, Text, DropdownMenu, Spinner, Grid } from "@radix-ui/themes";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { logout } from "@/2_features/auth/api/logout";
import { useUser } from "@/4_shared/hooks/useUser";
import { NavigationMenu } from "radix-ui";

export const Header = () => {
  const router = useRouter();
  const { user, loading, setUser } = useUser();

  const handleLogout = async () => {
    try {
      await logout();
      setUser(null);
      router.push("/login");
    } catch (error) {
      console.error("Logout failed:", error);
    }
  };

  return (
    <Grid className={styles.Container} gap="6" >
      <Box></Box>

      <NavigationMenu.Root className={styles.CenterSection}>
        <NavigationMenu.List className={styles.MenuList}>
          <NavigationMenu.Item>
            <Link href="/chat-bot" className={`${styles.Link} `}>
              Помощник
            </Link>
          </NavigationMenu.Item>
          <NavigationMenu.Item>
            <NavigationMenu.Trigger className={`${styles.Trigger}`}>
              Документы
              <CaretDownIcon className={styles.CaretDown} aria-hidden />
            </NavigationMenu.Trigger>
            <NavigationMenu.Content className={styles.Content}>
              <ul className={styles.SubList}>
                <li>
                  <Link
                    className={styles.SubLink}
                    href="/clinical-recomendation"
                  >
                    Клинические рекомендации
                  </Link>
                </li>
                <li>
                  <NavigationMenu.Link className={styles.SubLink} href="/url/documets">
                    Умный
                  </NavigationMenu.Link>
                </li>
              </ul>
            </NavigationMenu.Content>
          </NavigationMenu.Item>
        </NavigationMenu.List>
      </NavigationMenu.Root>

      <Box className={styles.RightSection}>
        {loading ? (
          <Spinner />
        ) : user ? (
          <DropdownMenu.Root>
            <DropdownMenu.Trigger>
              <Flex align="center" gap="2">
                <Flex direction="column" mr="1">
                  <Text size="3" color="gray" style={{ cursor: "pointer" }}>
                    {user.username}
                  </Text>
                </Flex>
                <CaretDownIcon />
              </Flex>
            </DropdownMenu.Trigger>

            <DropdownMenu.Content className={styles.DropdownContent}>
              <DropdownMenu.Item
                className={styles.DropdownItem}
                color="red"
                onClick={handleLogout}
                style={{ cursor: "pointer" }}
              >
                <ExitIcon className={styles.MenuIcon} />
                Выйти
              </DropdownMenu.Item>
            </DropdownMenu.Content>
          </DropdownMenu.Root>
        ) : (
          <Link href="/login" style={{ color: "var(--accent-10)" }}>
            Войти
          </Link>
        )}
      </Box>
    </Grid>
  );
};
