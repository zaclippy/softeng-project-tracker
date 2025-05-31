import { NumberInputStylesNames } from '@mantine/core';
import {
  Avatar,
  Badge,
  Table,
  Group,
  Text,
  Anchor,
  ScrollArea,
  useMantineTheme,
} from '@mantine/core';

interface ReqTableProps {
  data: {
    requirement_title: string;
    project_priority_level: string;
    core_feature: boolean;
    cost_to_fulfill: number;
    requirement_fulfilled: boolean;
  }[];
}

const roleColors: Record<string, string> = {
  low: 'gray',
  medium: 'yellow',
  high: 'green',
};

export function RequirementsTable({ data }: ReqTableProps) {
  const theme = useMantineTheme();
  const rows = data.map((item) => (
    <tr key={item.requirement_title}>
      <td>
        <Group spacing="sm">
          <Text fz="sm" fw={500}>
            {item.requirement_title}
          </Text>
        </Group>
      </td>
      <td>
        <Badge
          color={roleColors[item.project_priority_level.toLowerCase()]}
          variant={
            item.core_feature === true
              ? 'gradient' // if core feature, make it gradient
              : theme.colorScheme === 'dark'
              ? 'light'
              : 'outline'
          }
        >
          {item.project_priority_level}
        </Badge>
      </td>
      <td>
        <Anchor component={item.requirement_fulfilled ? 'a' : 'button'} size="sm">
          {item.requirement_fulfilled ? '✅' : '❌'}
        </Anchor>
      </td>
      <td>
        <Text fz="sm" c="dimmed">
          £{item.cost_to_fulfill}
        </Text>
      </td>
    </tr>
  ));

  return (
    <ScrollArea>
      <Table sx={{ minWidth: 800 }} verticalSpacing="sm">
        <thead>
          <tr>
            <th>Title</th>
            <th>Priority</th>
            <th>Fulfilled</th>
            <th>Cost</th>
            <th />
          </tr>
        </thead>
        <tbody>{rows}</tbody>
      </Table>
    </ScrollArea>
  );
}
