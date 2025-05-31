import { Badge, Divider, Group, Paper, Text, ThemeIcon } from '@mantine/core';
import { ComposedChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';
import { DatePicker } from '@mantine/dates';
import useSWR from 'swr';
import React from 'react';
import { IconSwimming } from '@tabler/icons';

interface Task {
  Task: string;
  'Recommended task start': number;
  'Recommended task duration (days)': number;
  'Recommended start date': Date;
}

interface MilestonesData {
  length: number;
  max: number;
  list: Task[];
}

export default function Milestones() {
  const fetcher = (url: string) => fetch(url).then((res) => res.json());

  const taskData = useSWR<MilestonesData>('http://127.0.0.1:5000/GanttChartData', fetcher);

  if (taskData.error) return <div>Failed to load task data</div>;

  if (!taskData.data) return <div>Loading task data</div>;

  return (
    <>
      <ComposedChart
        layout="vertical"
        width={900}
        height={400}
        data={taskData.data.list}
        margin={{
          top: 10,
          right: 20,
          bottom: 20,
          left: -10,
        }}
      >
        <CartesianGrid stroke="#f5f5f5" />
        <YAxis
          dataKey="Task"
          type="category"
          scale="band"
          tick={false}
          fontSize={10}
          label={{ value: 'Task (hover for more info)', position: '', offset: 0, angle: -90 }}
        />
        <XAxis
          type="number"
          scale="linear"
          fill="#808080"
          tick={true}
          domain={[0, taskData.data.max]}
          tickFormatter={(tick) => tick + ' days'}
          label={{ value: 'Days to complete', position: 'insideBottomRight', offset: 0 }}
        />
        <Tooltip /*Shows the data in an easy to read way when hovered*/ />
        {/* <Legend /> */}
        <Bar
          dataKey="Recommended task start"
          stackId="a"
          barSize={20}
          fill="rgba( 255, 255, 255, 0.0 )"
        />
        <Bar dataKey="Recommended task duration (days)" stackId="a" barSize={20} fill="#808080" />
        <Bar dataKey="Recommended start date" barSize={10} fill="#808080" />
      </ComposedChart>
      <Divider mt="sm" mb="sm" />
      <div>
        <Text size="xl" ta="center" sx={{ lineHeight: 2 }}>
          {' '}
          Current task{' '}
        </Text>
        <Paper radius="md">
          <Text ta="center" fw={700}>
            {taskData.data.list[0]['Task']}
          </Text>
          <Group position="center" mt="xs">
            <Badge size="md">4 days left</Badge>
          </Group>
        </Paper>
      </div>
      <Divider mt="sm" mb="sm" />
    </>
  );
}
