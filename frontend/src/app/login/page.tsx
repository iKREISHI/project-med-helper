import { LoginForm } from "@/2_features/auth";
import { Flex } from "@radix-ui/themes";

export default function Login() {
  return (
    <Flex align="center" justify="center" minHeight="calc(100vh - 60px)">
      <LoginForm />
    </Flex>
  );
}