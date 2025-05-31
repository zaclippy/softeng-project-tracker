import { useState } from 'react';
import {
  createStyles,
  Container,
  Avatar,
  UnstyledButton,
  Group,
  useMantineColorScheme,
  Text,
  Menu,
  Tabs,
  Modal,
  Burger,
  TextInput,
  NumberInput,
} from '@mantine/core';
import { useRouter } from 'next/router';
import { useDisclosure } from '@mantine/hooks';
import {
  IconLogout,
  IconChevronDown,
  IconAdjustments,
  IconMan,
  IconSun,
  IconMoonStars,
} from '@tabler/icons';
import { useForm } from '@mantine/form';
import { mutate } from 'swr';

const useStyles = createStyles((theme) => ({
  header: {
    paddingTop: theme.spacing.sm,
    backgroundColor: theme.colorScheme === 'dark' ? theme.colors.dark[6] : theme.colors.gray[0],
    borderBottom: `1px solid ${
      theme.colorScheme === 'dark' ? 'transparent' : theme.colors.gray[2]
    }`,
    marginBottom: 30,
  },

  mainSection: {
    paddingBottom: theme.spacing.sm,
  },

  user: {
    color: theme.colorScheme === 'dark' ? theme.colors.dark[0] : theme.black,
    padding: `${theme.spacing.xs}px ${theme.spacing.sm}px`,
    borderRadius: theme.radius.sm,
    transition: 'background-color 100ms ease',

    '&:hover': {
      backgroundColor: theme.colorScheme === 'dark' ? theme.colors.dark[8] : theme.white,
    },

    [theme.fn.smallerThan('xs')]: {
      display: 'none',
    },
  },

  burger: {
    [theme.fn.largerThan('xs')]: {
      display: 'none',
    },
  },

  userActive: {
    backgroundColor: theme.colorScheme === 'dark' ? theme.colors.dark[8] : theme.white,
  },

  tabs: {
    [theme.fn.smallerThan('sm')]: {
      display: 'none',
    },
  },

  tabsList: {
    borderBottom: '0 !important',
  },

  tab: {
    fontWeight: 500,
    height: 38,
    backgroundColor: 'transparent',

    '&:hover': {
      backgroundColor: theme.colorScheme === 'dark' ? theme.colors.dark[5] : theme.colors.gray[1],
    },

    '&[data-active]': {
      backgroundColor: theme.colorScheme === 'dark' ? theme.colors.dark[7] : theme.white,
      borderColor: theme.colorScheme === 'dark' ? theme.colors.dark[7] : theme.colors.gray[2],
    },
  },
}));

interface HeaderTabsProps {
  user: { name: string; image?: string };
  tabs: string[];
}

export function Header({ user, tabs }: HeaderTabsProps) {
  const { classes, cx } = useStyles();
  const { colorScheme, toggleColorScheme } = useMantineColorScheme();

  const [opened, { toggle }] = useDisclosure(false);

  const [userMenuOpened, setUserMenuOpened] = useState(false);
  const router = useRouter();

  const [selectedTab, setSelectedTab] = useState('Dashboard');

  const [openModal, setOpenModal] = useState(false);

  const handleTabSelect = (tab: string) => {
    setSelectedTab(tab);
    // Route to the right tab
    if (tab === 'Dashboard') {
      router.push('/');
    } else {
      router.push('/' + tab.charAt(0).toUpperCase() + tab.slice(1));
    }
  };

  const changeUser = async (newUser: { email: string; id: number }) => {
    // Make a post request with the new project data
    const res = await fetch('http://127.0.0.1:5000/ChangeEmployee', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(newUser),
    });
    // If successful, update the cache with the new project data
    if (res.ok) {
      mutate('http://127.0.0.1:5000/ChangeEmployee', newUser);
      window.location.reload();
    }
  };

  // Form for switching user
  const form = useForm({
    validate: {
      email: (value) =>
        /^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/.test(value.trim())
          ? null
          : 'Email is invalid',
      id: (value) => (Number.isInteger(value) ? null : 'ID must be a number'),
    },
    initialValues: {
      email: '',
      id: null,
    },
  });

  // submit handler to change the user
  const formOnSubmit = (vals: { email: string; id: number }) => {
    alert('User changed to ' + vals.email + ' with ID ' + vals.id);
    changeUser(vals); // change the user
    window.location.reload();
  };

  return (
    <div className={classes.header}>
      <Container className={classes.mainSection}>
        <Group position="apart">
          {/* <MantineLogo size={28} /> */}
          <Text weight={1000} size="xl" sx={{ lineHeight: 2 }} mr={4}>
            CS261 Group 34
          </Text>
          <Burger opened={opened} onClick={toggle} className={classes.burger} size="sm" />

          <Menu
            width={260}
            position="bottom-end"
            transition="pop-top-right"
            onClose={() => setUserMenuOpened(false)}
            onOpen={() => setUserMenuOpened(true)}
          >
            <Menu.Target>
              <UnstyledButton
                className={cx(classes.user, { [classes.userActive]: userMenuOpened })}
              >
                <Group spacing={7}>
                  <Avatar src={user.image} alt={user.name} radius="xl" size={20} />
                  <Text weight={500} size="sm" sx={{ lineHeight: 1 }} mr={3}>
                    {user.name}
                  </Text>
                  <IconChevronDown size={12} stroke={1.5} />
                </Group>
              </UnstyledButton>
            </Menu.Target>
            <Menu.Dropdown>
              <Menu.Label>Settings</Menu.Label>
              <Menu.Item icon={<IconAdjustments size={14} stroke={1.5} />}>Preferences</Menu.Item>

              <Menu.Label>Account</Menu.Label>
              <Menu.Item icon={<IconMan size={14} stroke={1.5} />}>Account Details</Menu.Item>
              <Menu.Item
                icon={<IconLogout size={14} stroke={1.5} />}
                onClick={() => {
                  setOpenModal(true);
                }}
              >
                Logout
              </Menu.Item>
              <Menu.Divider />
              <Menu.Item
                onClick={() => toggleColorScheme()}
                sx={(theme) => ({
                  backgroundColor:
                    theme.colorScheme === 'dark' ? theme.colors.dark[6] : theme.colors.gray[0],
                  color:
                    theme.colorScheme === 'dark' ? theme.colors.yellow[4] : theme.colors.blue[6],
                })}
                icon={
                  colorScheme === 'dark' ? (
                    <IconSun size={20} stroke={1.5} />
                  ) : (
                    <IconMoonStars size={20} stroke={1.5} />
                  )
                }
              >
                {colorScheme === 'dark' ? 'Light Mode' : 'Dark Mode'}
              </Menu.Item>
            </Menu.Dropdown>
          </Menu>
          <Modal
            opened={openModal}
            onClose={() => {
              setOpenModal(false); // closes the modal
              window.location.reload(); // reloads the page
            }}
          >
            {/* Render a form within the Modal component */}
            <form id="form" className="form" onSubmit={form.onSubmit(formOnSubmit)}>
              <h3>Switch user</h3>
              {/* <label htmlFor="user">Email</label> */}
              <TextInput label="Email" {...form.getInputProps('email')} />
              <NumberInput label="Employee ID" {...form.getInputProps('id')} />
              <button type="submit">Log In</button>
            </form>
          </Modal>
        </Group>
      </Container>
      <Container>
        <Tabs
          defaultValue={selectedTab}
          variant="outline"
          classNames={{
            root: classes.tabs,
            tabsList: classes.tabsList,
            tab: classes.tab,
          }}
          value={selectedTab}
          //   onTabChange={(value) => router.push(`/${value}`)}
          onTabChange={handleTabSelect}
        >
          <Tabs.List>
            {tabs.map((tab) => (
              <Tabs.Tab value={tab} key={tab}>
                {tab}
              </Tabs.Tab>
            ))}
          </Tabs.List>
        </Tabs>
      </Container>
    </div>
  );
}
