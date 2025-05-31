import { Header } from './Header';
import useSWR from 'swr'


interface AppShellProps {
  children: React.ReactNode;
}

// interface to define the shape of the data received from the flask api
interface HeaderData {
    username: string,
    manager: boolean,
}

export const AppShell = ({ children }: AppShellProps) => {
  // FETCHING DATA FOR THE TABS
  const fetcher = (url: string) => fetch(url).then((res) => res.json());

  const { data, error } = useSWR<HeaderData>('http://127.0.0.1:5000/HeaderData', fetcher);   // using the interface defined earlier as a type parameter when using the useSWR hook

  if (error) return <div>Failed to load data <br />{String(error)}</div>;
  if (!data) return <div>Loading data ... </div>;

  const user = {
    name: data.username,
  }; // user data

  // All tabs are available to the project manager, but only some are available if the user is not a manager.
  const tabs: string[] = data.manager ? ['Dashboard', 'Milestones', 'Tasks', 'Requirements', 'Team'] : ['Milestones', 'Tasks', 'Team'] ; // tabs data

  return (
    <>
      <Header user={user} tabs={tabs} />
      <main>{children}</main>
    </>
  );
};
