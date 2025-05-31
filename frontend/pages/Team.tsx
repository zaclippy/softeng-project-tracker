import { Text } from '@mantine/core';
import { UsersTable } from '../components/Users';
import useSWR from 'swr';

interface UserData {
  email: string;
  employee_id: number;
  first_name: string;
  last_name: string;
  phone: number;
  project_id: number;
  project_role: string;
}

interface UsersData {
  project_name: string;
  list: UserData[];
}

export default function Team() {
  const fetcher = (url: string) => fetch(url).then((res) => res.json());
  const { data, error } = useSWR<UsersData>('http://127.0.0.1:5000/Employees/Team', fetcher); // using the interface defined earlier as a type parameter when using the useSWR hook
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
      <Text size="xl" sx={{ lineHeight: 2 }}>
        {data.project_name} Team
      </Text>
      This will show skills, roles, projects managed of all employees - show who is on project and
      who isnt
      <br />
      <UsersTable
        data={
          data.list.map((row: UserData) => ({
            name: row.first_name + ' ' + row.last_name,
            role: row.project_role,
            email: row.email,
            phone: row.phone,
          }))
          // TODO add a button to click and view all skills
        }
      />
      <br />
      Todo here - Create and adjust all - Send request to a team member.
    </div>
  );
}
