"use client";
import {
  Box,
  Button,
  Callout,
  Flex,
  Heading,
  IconButton,
  Text,
  TextField,
} from "@radix-ui/themes";
import styles from "./loginForm.module.css";
import { useState } from "react";
import {
  EyeClosedIcon,
  EyeOpenIcon,
  InfoCircledIcon,
  LockClosedIcon,
  PersonIcon,
} from "@radix-ui/react-icons";
import { login } from "../api/login";
import { useRouter } from "next/navigation";
import { useAsync } from "@/4_shared";
import { useUser } from "@/4_shared/hooks/useUser";

export const LoginForm = () => {
  const [showPassword, setShowPassword] = useState(false);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const router = useRouter();
  const { refetchUser } = useUser();

  const handleLogin = async () => {
    await login({ username, password });
    await refetchUser();
    router.push("/");
  };

  const { loading, error, success, run } = useAsync(handleLogin);

  return (
    <Box className={styles.Container} m={{ initial: "4", lg: "0" }}>
      <Flex direction="column" gap="2" mb="5">
        <Heading>Вход</Heading>
        <Text color="gray" className={styles.Text}>
          Пожалуйста, введите ваш логин и пароль для доступа к системе
        </Text>
      </Flex>

      <form
        action=""
        method="post"
        onSubmit={(e) => {
          e.preventDefault();
          run();
        }}
      >
        <Flex direction="column" gap="3">
          {error && (
            <Callout.Root color="red" size="1">
              <Callout.Icon>
                <InfoCircledIcon />
              </Callout.Icon>
              <Callout.Text>{error}</Callout.Text>
            </Callout.Root>
          )}

          <TextField.Root
            placeholder="Введите логин"
            required
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            autoComplete="username"
          >
            <TextField.Slot>
              <PersonIcon />
            </TextField.Slot>
          </TextField.Root>

          <TextField.Root
            placeholder="Введите пароль"
            type={showPassword ? "text" : "password"}
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete="current-password"
          >
            <TextField.Slot>
              <LockClosedIcon />
            </TextField.Slot>
            <TextField.Slot>
              <IconButton
                size="2"
                variant="ghost"
                onClick={() => setShowPassword((show) => !show)}
                type="button"
                color="gray"
              >
                {showPassword ? (
                  <EyeOpenIcon aria-hidden />
                ) : (
                  <EyeClosedIcon aria-hidden />
                )}
              </IconButton>
            </TextField.Slot>
          </TextField.Root>

          <Button disabled={!username || !password || loading}>Войти</Button>
        </Flex>
      </form>
    </Box>
  );
};
