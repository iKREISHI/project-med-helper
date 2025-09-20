import * as React from "react";
import { NavigationMenu } from "radix-ui";
import { CaretDownIcon } from "@radix-ui/react-icons";
import styles from "./header.module.css";

export const Header = () => {
  return (
    <NavigationMenu.Root className={styles.Root}>
      <NavigationMenu.List className={styles.MenuList}>
        <NavigationMenu.Item>
          <NavigationMenu.Link className={styles.Link} href="/url/documets">
            Документы
          </NavigationMenu.Link>
        </NavigationMenu.Item>
        <NavigationMenu.Item>
          <NavigationMenu.Link className={styles.Trigger} href="/chat-bot">
            Помощник
          </NavigationMenu.Link>
        </NavigationMenu.Item>
      </NavigationMenu.List>
    </NavigationMenu.Root>
  );
};
