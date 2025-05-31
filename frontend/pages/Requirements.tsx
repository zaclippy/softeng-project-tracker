import { Text, Button, TextInput, Modal, NumberInput, Select } from '@mantine/core';
import { useForm } from '@mantine/form';
import { DatePicker } from '@mantine/dates';
import React, { useState } from 'react';
import useSWR, { mutate } from 'swr';
import { RequirementsTable } from '../components/RequirementsTable';
import { NumberControl } from '@mantine/ds/lib/Demo/Configurator/controls/NumberControl';

// interface to define the shape of the data received from the flask api
interface ReqData {
  requirement_title: string;
  project_priority_level: string;
  core_feature: boolean;
  cost_to_fulfill: number;
  requirement_fulfilled: boolean;
}

interface RequirementsData {
  project_name: string;
  list: ReqData[];
}

// --- SWR post for new requirement ---
// Define a function to create a new project
const addRequirement = async (newReq: ReqData) => {
  // Make a post request with the new project data
  const res = await fetch('http://127.0.0.1:5000/AddRequirement', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(newReq),
  });
  // If successful, update the cache with the new project data
  if (res.ok) {
    mutate('http://127.0.0.1:5000/AddRequirement', newReq); // update the project to the new one
    window.location.reload(); // reload the page to show the new project data
  }
};

export default function Requirements() {
  const [opened, setOpened] = useState(false);

  // Form for creating a new project
  const form = useForm({
    validate: {
      requirement_title: (value) => {
        if (!value) return 'Requirement name needed';
      },
      cost_to_fulfill: (value) => {
        if (!value) return 'Cost is required';
      },
    },
    initialValues: {
      requirement_title: '',
      cost_to_fulfill: 0,
      core_feature: false,
      project_priority_level: 'low',
    },
  });

  // form submit handler
  const formOnSubmit = (vals: {
    requirement_title: string;
    cost_to_fulfill: number;
    core_feature: boolean;
    project_priority_level: string;
  }) => {
    // Create a new requirement object
    const newReq: ReqData = {
      requirement_title: vals.requirement_title,
      cost_to_fulfill: vals.cost_to_fulfill,
      core_feature: vals.core_feature,
      project_priority_level: vals.project_priority_level,
      requirement_fulfilled: false,
    };
    // Add the new requirement to the database
    addRequirement(newReq);
  };

  // ---- SWR FETCHING DATA ----
  const fetcher = (url: string) => fetch(url).then((res) => res.json());
  const { data, error } = useSWR<RequirementsData>(
    'http://127.0.0.1:5000/Project/Requirements',
    fetcher
  ); // using the interface defined earlier as a type parameter when using the useSWR hook
  if (error)
    return (
      <div>
        Failed to load data <br />
        {String(error)}
      </div>
    );
  if (!data) return <div>Loading data ... </div>;

  return (
    <div>
      <Text
        sx={{ fontFamily: 'Greycliff CF, sans-serif', lineHeight: 2 }}
        ta="center"
        fz="xl"
        fw={600}
      >
        Requirements for {data.project_name}
      </Text>

      <div>
        <RequirementsTable
          data={
            data.list.map((row: ReqData) => ({
              requirement_title: row.requirement_title,
              project_priority_level: row.project_priority_level,
              core_feature: row.core_feature,
              cost_to_fulfill: row.cost_to_fulfill,
              requirement_fulfilled: row.requirement_fulfilled,
            }))
            // TODO add a button to click and view all skills
          }
        />
        {/* BUTTON: */}
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
          <Button
            variant="gradient"
            gradient={{ from: 'cyan', to: 'green' }}
            onClick={() => setOpened(true)} // Button opens a popup
          >
            New Requirement
          </Button>
          {/* Popup from new project: */}
          <Modal opened={opened} onClose={() => setOpened(false)} title="Add a task" size="lg">
            <form onSubmit={form.onSubmit(formOnSubmit)}>
              <TextInput label="Requirement name" {...form.getInputProps('requirement_title')} />
              <Select
                label="Priority"
                placeholder="Select priority"
                data={['Low', 'Medium', 'High']}
                {...form.getInputProps('project_priority_level')}
              />
              <Select
                label="Core feature"
                placeholder="Select priority"
                data={['Yes', 'No']}
                {...form.getInputProps('core_feature')}
              />
              <NumberInput label="Cost in £" {...form.getInputProps('cost_to_fulfill')} />
              {/* Create a new requirement here */}
              <br /> <Button type="submit">Create requirements</Button>
            </form>
          </Modal>
          <br />
        </div>
      </div>
    </div>
  );
}
