import * as React from "react";
import { NavigationMenu } from "radix-ui";
import { CaretDownIcon } from "@radix-ui/react-icons";
import styles from "./header.module.css";

export const Header = () => {
  return (
    <NavigationMenu.Root className={styles.Root}>
      <NavigationMenu.List className={styles.MenuList}>
        <NavigationMenu.Item>
          <NavigationMenu.Link className={styles.Link} href="#">
            Документы
          </NavigationMenu.Link>
        </NavigationMenu.Item>
        <NavigationMenu.Item>
          <NavigationMenu.Trigger className={styles.Trigger}>
            Помощник
            <CaretDownIcon className={styles.CaretDown} aria-hidden />
          </NavigationMenu.Trigger>
          <NavigationMenu.Content className={styles.Content}>
            <ul className={styles.SubList}>
              <li>
                <NavigationMenu.Link className={styles.SubLink} href="#">
                  Тупой
                </NavigationMenu.Link>
              </li>
              <li>
                <NavigationMenu.Link className={styles.SubLink} href="#">
                  Умный
                </NavigationMenu.Link>
              </li>
            </ul>
          </NavigationMenu.Content>
        </NavigationMenu.Item>
      </NavigationMenu.List>
    </NavigationMenu.Root>
  );
};
