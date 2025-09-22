"use client";
import * as React from "react";
import { CaretDownIcon, ExitIcon } from "@radix-ui/react-icons";
import styles from "./header.module.css";
import { Box, Flex, Text, DropdownMenu, Spinner } from "@radix-ui/themes";
import { useRouter, usePathname } from "next/navigation";
import Link from "next/link";
import { logout } from "@/2_features/auth/api/logout";
import { useUser } from "@/4_shared/hooks/useUser";

export const Header = () => {
  const router = useRouter();
  const pathname = usePathname();
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

  const menuItems = [
    { href: "/url/documets", label: "Документы" },
    { href: "/chat-bot", label: "Помощник" },
  ];

  return (
    <Flex className={styles.Container} gap="6">
      <Box></Box>

      <Box className={styles.CenterSection}>
        <Flex gap={{ initial: "3", lg: "7" }} align="center">
          {menuItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={`${styles.Link} ${
                pathname === item.href ? styles.ActiveLink : ""
              }`}
            >
              {item.label}
            </Link>
          ))}
        </Flex>
      </Box>

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
    </Flex>
  );
};
