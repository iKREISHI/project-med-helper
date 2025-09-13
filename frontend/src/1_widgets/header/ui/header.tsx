import * as React from 'react'
import { NavigationMenu } from "radix-ui";
import Link from 'next/link'
import classNames from "classnames";
import styles from './header.module.css'
import { CaretDownIcon } from '@radix-ui/react-icons' 



export function Header() {
  return (
    <NavigationMenu.Root className={styles.Root}>
      <NavigationMenu.List className={styles.MenuList}>
        <NavigationMenu.Item>
        <NavigationMenu.Trigger
          className={styles.Trigger}
        >
          Че-то еще <CaretDownIcon/>
        </NavigationMenu.Trigger>
      </NavigationMenu.Item>
      <NavigationMenu.Item>
        <NavigationMenu.Trigger className={styles.Trigger}>
          Документы <CaretDownIcon />
        </NavigationMenu.Trigger>
        <NavigationMenu.Content className={styles.Content}>
          <ul className={`${styles.List} two`}>
            <li>
              Отчеты
            </li>
          </ul>
        </NavigationMenu.Content>
      </NavigationMenu.Item>
      <NavigationMenu.Item>
        <NavigationMenu.Trigger
        className={styles.Trigger}
        >
          Помощник <CaretDownIcon />
        </NavigationMenu.Trigger>
      </NavigationMenu.Item>
    </NavigationMenu.List>
    </NavigationMenu.Root>
  )
}