import { DashboardContainer } from "@/4_shared";
import { BookmarkIcon } from "@radix-ui/react-icons";
import { Badge, Flex, Text } from "@radix-ui/themes";

export const Bookmarks = () => {
  return (
    <DashboardContainer>
      <Flex align="center" gap="2">
        <Badge size="2" color="gray">
          <BookmarkIcon />
          <Text>Закладки</Text>
        </Badge>
      </Flex>
      <Flex align="center" justify="center" height="100%">
        <Text style={{ fontStyle: "italic" }} color="gray">
          Пусто
        </Text>
      </Flex>
    </DashboardContainer>
  );
};
