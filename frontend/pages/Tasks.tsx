import { Text, Button, Modal, TextInput, ActionIcon, Table, Textarea, NumberInput, Select } from '@mantine/core';
import { useForm } from '@mantine/form';
import { DatePicker } from '@mantine/dates';
import React, { useState } from 'react';
import useSWR, { mutate } from 'swr'
import { IconAdjustments, IconCheck } from '@tabler/icons';

// interface to define the shape of the data received from the flask api
interface TaskData {
    id: number;
    name: string;
    finished: boolean;
    deadline: string;
    description: string;
}

interface ReqData {
  requirement_title: string;
  requirement_id: number;
  project_priority_level: string;
  core_feature: boolean;
  cost_to_fulfill: number;
  requirement_fulfilled: boolean;
}

interface RequirementsData {
  project_name: string;
  list: ReqData[];
}

interface NewTaskData {
  name: string;
  deadline: string; // deadline is a string in the format "YYYY-MM-DD" to avoid conflicts with the flask API and sql types 
  description: string;
  requirementID: number;
}

interface TasksData {
  project_name: string;
  list: TaskData[];
}

// --- SWR post for new task ---
// Define a function to create a new task
const addTask = async (newTask: NewTaskData) => {
  // Make a post request with the new project data
  const res = await fetch('http://127.0.0.1:5000/AddTask', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(newTask),
  });
  // If successful, update the cache with the new project data
  if (res.ok) {
    mutate('http://127.0.0.1:5000/AddTask', newTask); 
      window.location.reload(); // reload the page to show the new project data
    }
  }

  // ASSIGN A TASK TO A NEW EMPLOYEE
  const assignTask = async (data: {task_id: number, employee_id: number}) => {
    // Make a post request with the new project data
    const res = await fetch('http://127.0.0.1:5000/AssignTask', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    })
    if (res.ok) {
      mutate('http://127.0.0.1:5000/AssignTask', data); // assign the task to the employee
      window.location.reload(); // reload the page to show the new project data
    }
  }

  // User to mark a task as complete
  const completeTask = async (data: {task_id: number}) => {
    // Make a post request with the new project data
    const res = await fetch('http://127.0.0.1:5000/CompleteTask', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    })
    if (res.ok) {
      mutate('http://127.0.0.1:5000/CompleteTask', data); // assign the task to the employee
    window.location.reload(); // reload the page to show the new project data
  }
};

export default function Tasks() {
  const [opened, setOpened] = useState(false);

  // Form for creating a new project
  const form = useForm({
    validate: {
      name: value => {
        if (!value) return 'Task name is required';
      },
      deadline: value => {
        if (!value) return 'Deadline is required';
      }
    },
    initialValues: {
      name: '',
      description: '',
      deadline: null,
      requirementID: 0,
    }
  })

  // form submit handler
  const formOnSubmit = (vals: {
    name: string;
    description: string;
    deadline: Date;
    requirementID: number;
  }) => {
    // Create a new requirement object
    const newTask: NewTaskData = {
      name: vals.name,
      description: vals.description,
      deadline: vals.deadline.toISOString(),
      requirementID: Number(String(vals.requirementID).split(" ")[0]),
    };
    // Add the new requirement to the database
    addTask(newTask);
  };

  // ---- SWR FETCHING DATA ----
  const fetcher = (url: string) => fetch(url).then((res) => res.json());

  const requirements = useSWR<RequirementsData>(
    'http://127.0.0.1:5000/Project/Requirements',
    fetcher
  );

  const tasks = useSWR<TasksData>('http://127.0.0.1:5000/Project/TasksDisplay', fetcher);   // using the interface defined earlier as a type parameter when using the useSWR hook
  
  if (tasks.error) return <div>Failed to load data</div>;
  if (!tasks.data) return <div>Loading data ... </div>;

  return (
    <div>
      <Text
        sx={{ fontFamily: 'Greycliff CF, sans-serif', lineHeight: 2 }}
        ta="center"
        fz="xl"
        fw={600}
      >
        Tasks for {tasks.data.project_name}
      </Text>

      <div>
        <Table miw={700}>
          <thead>
            <tr>
              <th>Name</th>
              <th>Description</th>
              <th>Deadline</th>
              <th>Finished</th>
            </tr>
          </thead>
          <tbody>
            {tasks.data.list.map((row: TaskData) => (
              <tr key={row.name}>
                <td>{row.name}</td>
                <td>{row.description}</td>
                <td>{String(row.deadline)}</td>
                <td>{row.finished ? (
                "✅"
                  ) : (
                    <ActionIcon variant="default" onClick={() => {
                        completeTask({task_id: row.id})
                    }}>
                        <IconAdjustments size="1.125rem" />
                    </ActionIcon>
                )}</td>
            </tr>))
            }
        </tbody>
      </Table>
      {/* BUTTON: */}
      <div style={{ display: 'flex', justifyContent:'center', alignItems:'center' }}>
        <Button 
          variant="gradient" gradient={{ from: 'cyan', to: 'green' }}
          onClick={() => setOpened(true)}  // Button opens a popup
        > New Task </Button>
        {/* Popup from new project: */}
        <Modal opened={opened} onClose={() => setOpened(false)} title="Add a task" size="lg">
          <form onSubmit={form.onSubmit(formOnSubmit)}>
            <TextInput label="Task name" {...form.getInputProps('name')} />
            <Textarea label="Description" {...form.getInputProps('description')} />
            <DatePicker label="Deadline" placeholder="Click to select a date" {...form.getInputProps('deadline')}/>
            <Select label="Requirement ID" placeholder="Select requirement" data={
                requirements.data?.list.map((row: ReqData) => (
                    row.requirement_id + " " + row.requirement_title
                ))
            } {...form.getInputProps('requirementID')}/>
            {/* Assign to members */}
            <br /> <Button type="submit">Create task</Button>
          </form>
        </Modal>
        <br />
      </div>
      </div>
    </div>
  );
}
