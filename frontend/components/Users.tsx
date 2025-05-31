import {
  Avatar,
  Badge,
  Table,
  Group,
  Text,
  ActionIcon,
  Anchor,
  ScrollArea,
  useMantineTheme,
} from '@mantine/core';
import { IconEdit, IconSend } from '@tabler/icons';

interface UsersTableProps {
  data: { name: string; role: string; email: string; phone: string }[];
}

const roleColors: Record<string, string> = {
  un: 'gray', // unassigned
  fr: 'green', // front end
  ba: 'blue', // back end
  ml: 'cyan', // machine learning
  ma: 'yellow',
};

const roles = ['un', 'fr', 'ba', 'ml', 'ma'];

export function UsersTable({ data }: UsersTableProps) {
  const theme = useMantineTheme();
  const rows = data.map((item) => (
    <tr key={item.name}>
      <td>
        <Group spacing="sm">
          <Avatar size={30} src={''} radius={30} />
          <Text fz="sm" fw={500}>
            {item.name}
          </Text>
        </Group>
      </td>
      <td>
        <Badge
          color={item.role ? roleColors[item.role.toLowerCase().substring(0, 2)] : 'gray'}
          variant={
            item.role.toLowerCase() === 'manager'
              ? 'gradient' // if manager, make it gradient gold
              : theme.colorScheme === 'dark'
              ? 'light'
              : 'outline'
          }
        >
          {item.role}
        </Badge>
      </td>
      <td>
        <Anchor component="button" size="sm">
          {item.email}
        </Anchor>
      </td>
      <td>
        <Text fz="sm" c="dimmed">
          {item.phone}
        </Text>
      </td>
      <td>
        <Group spacing={0} position="right">
          <ActionIcon>
            <IconEdit size="1rem" stroke={1.5} />
          </ActionIcon>
          <ActionIcon color="orange">
            <IconSend size="1rem" stroke={1.5} />
          </ActionIcon>
        </Group>
      </td>
    </tr>
  ));

  return (
    <ScrollArea>
      <Table sx={{ minWidth: 800 }} verticalSpacing="sm">
        <thead>
          <tr>
            <th>Employee</th>
            <th>Role</th>
            <th>Email</th>
            <th>Phone</th>
            <th />
          </tr>
        </thead>
        <tbody>{rows}</tbody>
      </Table>
    </ScrollArea>
  );
}
