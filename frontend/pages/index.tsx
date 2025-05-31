import { StatsGrid, StatsProps } from '../components/Dashboard/StatsGrid';
import { LineChart, Line, CartesianGrid, XAxis, YAxis, PieChart, Pie } from 'recharts';
import {
  Text,
  Button,
  Space,
  Modal,
  TextInput,
  NumberInput,
  SegmentedControl,
  Tooltip,
} from '@mantine/core';
import { useForm } from '@mantine/form';
import { DatePicker } from '@mantine/dates';
import useSWR, { mutate } from 'swr';
import { useState } from 'react';
import { StatsGroup } from '../components/CodeStats';
import { BudgetStats } from '../components/BudgetStats';

type Code = {
  title: string;
  result: string;
  comment: string;
};

// interface to define the shape of the data received about the project from the flask api
interface DashboardData {
  project_name: string;
  switch_projects: string[];
  deadline: string;
  remaining_days: number;
  risk: number;
  readiness: number;
  budget: number;
  remaining_budget: number;
}

interface GitData {
  code: Code[];
}

interface EstimateData {
  title: string;
  stats: string;
  description: string;
}

interface EstimatesData {
  project_risk: number;
  estimates: EstimateData[];
}

// type for defining switch project
type SwitchProjectType = {
  project_name: string;
};

interface TaskCompletion {
  percentage_completed_tasks: number;
  total_number_of_completed_tasks: number;
  total_number_of_employee_tasks: number;
}

type RatingRange = 1 | 2 | 3 | 4 | 5;

interface FormData {
  projectName: string;
  projectType: string;
  deadline: Date;
  budget: number;
  teamSize: number;
  monthlySalary: number;
  projectClientName: string;
  requirements: number;
  // cocomoInputs: number[];
  RS: RatingRange; // 1 = very low, 5 = very high -- see what all the abbreviations stand for in the comments below where the form initialValues are defined
  SD: RatingRange;
  complexity: RatingRange;
  experience: RatingRange;
  PL: RatingRange;
  ST: RatingRange;
  DS: RatingRange;
  LOC: number;
  LOC2: number;
}

interface NewProjData {
  projectName: string;
  projectType: string;
  projectClientName: string;
  budget: number;
  deadline: Date;
  cocomoInputs: any[];
}

export default function HomePage() {
  // React state (useState hook) for the button opening a popup (using modal component):
  const [opened2, setOpened2] = useState(false);
  const [opened, setOpened] = useState(false);

  // Form for creating a new project
  // data received: [teamSize, monthlySalary, budget, deadline, requirements, RS, SD, complexity, experience, PL, ST, DS, LOC, LOC2]
  const form = useForm({
    validate: {
      projectName: (value) => (value.trim().length > 0 ? null : 'Project name is required'),
      teamSize: (value) => (value > 0 ? null : 'Team size must be a positive number'),
      monthlySalary: (value) => (value >= 0 ? null : 'Monthly salary must be a positive number'),
      budget: (value) => (value >= 0 ? null : 'Budget must be a positive number'),
      deadline: (value) => (value instanceof Date ? null : 'Deadline must be a valid date'),
    },
    initialValues: {
      projectName: 'New Project',
      projectClientName: 'Client A',
      projectType: 'Software',
      teamSize: 0,
      monthlySalary: 0,
      budget: 0,
      deadline: null,
      requirements: 0,
      //   cocomoInputs
      RS: 1, // required software reliability
      SD: 1, // software database size
      complexity: 1, // complexity of the product
      experience: 1, // analyst capability
      PL: 1, // programming language
      ST: 1, // software tools usage
      DS: 1, // development schedule
      LOC: 1, // lines of code
      LOC2: 1, // lines of code for reuse
    },
  });

  const numbers = [1, 2, 3, 4, 5];

  // Define a function to create a new project
  const newProject = async (newProject: NewProjData) => {
    // Make a post request with the new project data
    const res = await fetch('http://127.0.0.1:5000/AddProject', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(newProject),
    });
    // If successful, update the cache with the new project data
    if (res.ok) {
      mutate('http://127.0.0.1:5000/AddProject', newProject); // update the project to the new one
      window.location.reload(); // reload the page to show the new project data
    }
  };

  // submit the form for creating a new function
  const formOnSubmit = (vals: FormData) => {
    // Create a new project object
    const projData: NewProjData = {
      projectName: vals.projectName,
      projectType: vals.projectType,
      projectClientName: vals.projectClientName,
      budget: vals.budget,
      deadline: vals.deadline,
      // these are given in the format that the cocomo algorithm in initialAssessment.py expects
      cocomoInputs: [
        vals.teamSize,
        vals.monthlySalary,
        vals.budget,
        vals.deadline.toLocaleDateString(),
        vals.requirements,
        vals.RS,
        vals.SD,
        vals.complexity,
        vals.experience,
        vals.PL,
        vals.ST,
        vals.DS,
        vals.LOC,
        vals.LOC2,
      ],
      // input format - [teamSize, monthlySalary, budget, deadline, requirements, RS, SD, complexity, experience, PL, ST, DS, LOC, LOC2]
    };
    // alert(JSON.stringify(newProject));
    // Call the newProject function to create a new project
    newProject(projData);
  };

  // ---- SWR FETCHING DATA ----
  // Define a fetcher function that sends a post request
  const fetcher = (url: string) => fetch(url).then((res) => res.json());

  // Define a function to make a post request and update the cache
  const changeProject = async (newProject: SwitchProjectType) => {
    // Make a post request with the new project data
    const res = await fetch('http://127.0.0.1:5000/ChangeProject', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(newProject),
    });
    // If successful, update the cache with the new project data
    if (res.ok) {
      mutate('http://127.0.0.1:5000/ChangeProject', newProject); // update the project to the new one
      window.location.reload(); // reload the page to show the new project data
    }
  };

  const addProject = useSWR<{ cocomo: string }>(
    'http://127.0.0.1:5000/Project/AddProject',
    fetcher
  );

  const taskCompletionRate = useSWR<TaskCompletion>(
    'http://127.0.0.1:5000/Project/CompletedTasks',
    fetcher
  );

  // Assuming the flask api has an endpoint /api/budget that returns a JSON object with a budget property. When the HomePage component mounts, uses the useSWR hook to fetch data from this endpoint, returning an object with data and error property.
  const dashboard = useSWR<DashboardData>('http://127.0.0.1:5000/DashboardData', fetcher); // using the interface defined earlier as a type parameter when using the useSWR hook

  const gitData = useSWR<GitData>('http://127.0.0.1:5000/GitData', fetcher);

  const EstimateData = useSWR<EstimatesData>('http://127.0.0.1:5000/Estimates', fetcher);


  if (taskCompletionRate.error) return <div>Failed to load task completion data</div>;

  if (!taskCompletionRate.data) return <div>Loading task completion data</div>;

  if (addProject.data) {
    alert(addProject.data.cocomo);
    return (
      <>
        You have created a new project.
        <br />
      </>
    );
  }

  if (dashboard.error) return <div>Failed to load dashboard data</div>;

  if (!dashboard.data) return <div>Loading data ... </div>;

  // Placeholder data for the stat0istics grid shown on the dashboard
  const risk : number = EstimateData.data?.project_risk;
  const readiness = dashboard.data.readiness;
  
  const riskData: StatsProps = {
    title: 'Project Risk',
    icon: 'risk',
    value: (risk ? String(risk) + "%": "Loading..."),
    diff: risk ? (
        risk>=75 ? 4 : 
        risk>=50 ? 3 :
        risk>=25 ? 2 :
        1 
    ): 0,
  };
  const readyData: StatsProps = {
    title: 'Project Readiness',
    icon: 'ready',
    value: String(readiness) + '%',
    diff: readiness ? (
        readiness>=99 ? 4 : 
        readiness>=60 ? 3 :
        readiness>=30 ? 2 :
        1 
    ): 0,
  };
  const codeData: StatsProps = {
    title: 'Deadline',
    icon: 'time',
    value: String(dashboard.data.deadline),
    diff: dashboard.data.remaining_days,
  };
  const budgetData: StatsProps = {
    title: 'Budget Remaining / Total Budget',
    icon: 'budget',
    value: '£' + String(dashboard.data.remaining_budget) + ' / £' + String(dashboard.data.budget),
    diff: (100 * dashboard.data.remaining_budget) / dashboard.data.budget,
  };
  const lineChartData = [
    { name: 'Quarter 1', uv: taskCompletionRate.data.percentage_completed_tasks * (1 / 10) },
    { name: 'Quarter 2', uv: taskCompletionRate.data.percentage_completed_tasks * (1 / 3) },
    { name: 'Quarter 3', uv: taskCompletionRate.data.percentage_completed_tasks * (3 / 4) },
    { name: 'Quarter 4', uv: taskCompletionRate.data.percentage_completed_tasks },
  ];

  // The list of projects that can be selected
  const myProjects = dashboard.data.switch_projects;

  const comments: Code[] =
    gitData.data && !gitData.error
      ? gitData.data.code
      : [{ title: 'Loading', result: 'Loading', comment: 'Loading' }];

  const estimateForms: EstimateData[] =
  EstimateData.data && !EstimateData.error
    ? EstimateData.data.estimates
    : [{ title: 'Loading', stats: 'Loading', description: 'Loading' }];
  // the list of github api comments to be displayed
  const m = Math.ceil((comments.length-1)/ 2); // for splitting the list later - need to take one away because of the extra risk value at the end
  return (
    <div>
      <Text
        sx={{ fontFamily: 'Greycliff CF, sans-serif', lineHeight: 2 }}
        ta="center"
        fz="xl"
        fw={600}
      >
        {dashboard.data.project_name}
      </Text>
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
        <Space w="md" />
        <Button
          variant="gradient"
          gradient={{ from: 'blue', to: 'indigo' }}
          onClick={() => setOpened2(true)}
        >
          Switch Project
        </Button>
        <Modal
          opened={opened2}
          onClose={() => setOpened2(false)}
          title="All your projects:"
          size="sm"
        >
          {myProjects.map((proj) => (
            <Button
              key={proj}
              variant="outline"
              color="dark"
              onClick={() => {
                changeProject({
                  project_name: proj,
                });
              }}
            >
              {proj}
            </Button>
          ))}
        </Modal>
        <Space w="md" />
        <Button
          variant="gradient"
          gradient={{ from: 'cyan', to: 'green' }}
          onClick={() => setOpened(true)} // Button opens a popup
        >
          New Project
        </Button>
        {/* Popup from new project: */}
        <Modal
          opened={opened}
          onClose={() => setOpened(false)}
          title="Start a new Project"
          size="lg"
        >
          <form className="form" onSubmit={form.onSubmit(formOnSubmit)}>
            <TextInput label="Project name" required {...form.getInputProps('projectName')} />
            <TextInput label="Project type" required {...form.getInputProps('projectType')} />
            <DatePicker
              label="Deadline"
              required
              placeholder="Click to select a date"
              {...form.getInputProps('deadline')}
            />
            <TextInput label="Budget" {...form.getInputProps('budget')} />
            <NumberInput label="Team size" {...form.getInputProps('teamSize')} />
            <NumberInput label="Monthly salary" {...form.getInputProps('monthlySalary')} />
            <TextInput label="Project client name" {...form.getInputProps('projectClientName')} />
            <Text size="sm">
              Please predict the following project information, ranking from low to high
            </Text>
            {/* Render the segments array dynamically using map */}
            <table>
              <tr>
                <td>Required Software reliability</td>
                <td>
                  <SegmentedControl
                    data={numbers.map((n) => String(n))}
                    {...form.getInputProps('RS')}
                  />
                </td>
              </tr>
              <tr>
                <td>Software Database size</td>
                <td>
                  <SegmentedControl
                    data={numbers.map((n) => String(n))}
                    {...form.getInputProps('SD')}
                  />
                </td>
              </tr>
              <tr>
                <td>Complexity</td>
                <td>
                  <SegmentedControl
                    data={numbers.map((n) => String(n))}
                    {...form.getInputProps('complexity')}
                  />
                </td>
              </tr>
              <tr>
                <td>Experience</td>
                <td>
                  <SegmentedControl
                    data={numbers.map((n) => String(n))}
                    {...form.getInputProps('experience')}
                  />
                </td>
              </tr>
              <tr>
                <td>Programming Language</td>
                <td>
                  <SegmentedControl
                    data={numbers.map((n) => String(n))}
                    {...form.getInputProps('PL')}
                  />
                </td>
              </tr>
              <tr>
                <td>Software tools usage</td>
                <td>
                  <SegmentedControl
                    data={numbers.map((n) => String(n))}
                    {...form.getInputProps('ST')}
                  />
                </td>
              </tr>
              <tr>
                <td>Development Schedule</td>
                <td>
                  <SegmentedControl
                    data={numbers.map((n) => String(n))}
                    {...form.getInputProps('DS')}
                  />
                </td>
              </tr>
            </table>
            <NumberInput label="Requirements" {...form.getInputProps('requirements')} />
            <NumberInput label="Number of classes" {...form.getInputProps('LOC')} />
            <NumberInput label="Number of methods" {...form.getInputProps('LOC2')} />
            <button type="submit">Submit</button>
          </form>
        </Modal>
      </div>

      <StatsGrid data={[riskData, readyData, codeData, budgetData]} />
      <br />
      <div>
        <Text
          sx={{ fontFamily: 'Greycliff CF, sans-serif', lineHeight: 2 }}
          ta="center"
          fz="xl"
          fw={600}
        >
          Code analysis
        </Text>
        {/* first half */}
        {gitData.data && !gitData.error ? (
          <>
            <StatsGroup
              data={comments.splice(0, m).map((code) => ({
                title: code[0],
                stats: code[1],
                description: code[2],
              }))}
            />
            <Space h="xs" />
            <StatsGroup
              data={comments.slice(-(m+1), -1).map((code) => ({
                title: code[0],
                stats: code[1],
                description: code[2],
              }))}
            />
          </>
        ) : (
          'Loading...'
        )}
      </div>
      <br />
      <div>
        <Text
          sx={{ fontFamily: 'Greycliff CF, sans-serif', lineHeight: 2 }}
          ta="center"
          fz="xl"
          fw={600}
        >
          Budget analysis
        </Text>
        {/* first half */}
        {EstimateData.data && !EstimateData.error ? (
          <>
            <BudgetStats
              data={estimateForms.slice(-(m+1), m).map((code) => ({
                title: code[0],
                stats: code[1],
                description: code[2],
              }))}
            />

          </>
        ) : (
          'Loading...'
        )}
      </div>
      <br />
      <div>
        <Text
          sx={{ fontFamily: 'Greycliff CF, sans-serif', lineHeight: 2 }}
          ta="center"
          fz="xl"
          fw={600}
        >
          Tasks completed
        </Text>
        <br />
        <LineChart
          width={750}
          height={320}
          margin={{ top: 3, right: 80, bottom: 2, left: 180 }}
          data={lineChartData}
        >
          <Line type="monotone" dataKey="uv" stroke="#8884d8" />
          <CartesianGrid stroke="#ccc" strokeDasharray="5 5" />
          <XAxis dataKey="name" />
          <YAxis />
        </LineChart>
      </div>
    </div>
  );
}
