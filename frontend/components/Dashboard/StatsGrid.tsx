import { Badge, createStyles, Group, Paper, SimpleGrid, Text } from '@mantine/core';
import {
  IconCoin,
  IconArrowUpRight,
  IconArrowDownRight,
  IconAlertTriangle,
  IconTimelineEvent,
  IconCode,
  IconSeparatorHorizontal,
  IconClock,
} from '@tabler/icons';
//import { LineChart, Line } from 'recharts';

const useStyles = createStyles((theme) => ({
  root: {
    padding: theme.spacing.xl * 1.5,
  },

  value: {
    fontSize: 24,
    fontWeight: 700,
    lineHeight: 1,
  },

  diff: {
    lineHeight: 1,
    display: 'flex',
    alignItems: 'center',
  },

  icon: {
    color: theme.colorScheme === 'dark' ? theme.colors.dark[3] : theme.colors.gray[4],
  },

  title: {
    fontWeight: 700,
    textTransform: 'uppercase',
  },
}));

const icons = {
  risk: IconAlertTriangle,
  ready: IconTimelineEvent,
  code: IconCode,
  budget: IconCoin,
  time: IconClock,
};

// Type for the stats grid on the dashboard 
export interface StatsProps {
  title: string;
  icon: 'risk' | 'ready' | 'code' | 'budget' | 'time';
  value: string;
  diff: number;
}

// the comment written inside the badge
const riskBadge : (diff: number) => string = (diff) => {
    switch (diff) {
        case 0:
            return "Unknown";
        case 1:
            return "Low";
        case 2:
            return "Medium";
        case 3:
            return "High";
        case 4:
            return "Very high";
    }
}

// the comment written inside the badge
const readyBadge : (diff: number) => string = (diff) => {
    switch (diff) {
        case 0:
            return "";
        case 1:
            return "Getting started";
        case 2:
            return "Making progress";
        case 3:
            return "Almost Ready";
        case 4:
            return "Ready";
    }
}


export interface StatsGridProps {
  data: StatsProps[];
}

const Stats = (stat: StatsProps) => {
  const { classes } = useStyles();
  const Icon = icons[stat.icon];

  let DiffIcon;
  if (stat.diff == 0) {
    DiffIcon = IconSeparatorHorizontal;
  } else if (stat.diff > 0) {
    DiffIcon = IconArrowUpRight;
  } else {
    DiffIcon = IconArrowDownRight;
  }

  let statColor = 'grey';
  if (stat.diff > 0) {
    statColor = 'teal';
  } else if (stat.diff < 0) {
    statColor = 'red';
  }

  return (
    <Paper withBorder p="md" radius="md" key={stat.title}>
      <Group position="apart">
        <Text size="xs" color="dimmed" className={classes.title}>
          {stat.title}
        </Text>
        <Icon className={classes.icon} size={22} stroke={1.5} />
      </Group>

      <Group align="flex-end" spacing="xs" mt={15}>
        <Text className={classes.value}>{stat.value}</Text>
       {/* <Text color={statColor} size="sm" weight={400} className={classes.diff}>
          <span>{stat.diff == 0 ? '' : stat.diff + '%'}</span>
          <DiffIcon size={16} stroke={1.5} />
        </Text> */}
        { // show time remaining for deadline
          (stat.title == 'Deadline') ? <Group position="center" mt="xs">
            <Badge size="md">{stat.diff} days left</Badge>
        </Group>: 
        // show budget percentage for budget
        (stat.title == 'Budget Remaining / Total Budget') ? <Group position="center" mt="xs">
             <Badge size="md">{stat.diff} % left</Badge>
        </Group>:
        (stat.title == 'Project Risk') ? <Group position="center" mt="xs">
             <Badge size="md">{
             riskBadge(stat.diff)
             } risk</Badge>
        </Group>:
        (stat.title == 'Project Readiness') ? <Group position="center" mt="xs">
             <Badge size="md">{
             readyBadge(stat.diff)
             }</Badge>
        </Group>:
        <></>
        // <Text color={statColor} size="sm" weight={400} className={classes.diff}>
        //   <span>{stat.diff == 0 ? '' : stat.diff + '%'}</span>
        //   <DiffIcon size={16} stroke={1.5} />
        // </Text>
      }
      </Group>
    </Paper>
  );
};

export function StatsGrid({ data }: StatsGridProps) {
  const { classes } = useStyles();

  return (
    <div className={classes.root}>
      <SimpleGrid
        cols={4}
        breakpoints={[
          { maxWidth: 'md', cols: 2 },
          { maxWidth: 'xs', cols: 1 },
        ]}
      >
        {data.map((stat) => (
          <Stats {...stat} />
        ))}
      </SimpleGrid>
    </div>
  );
}
