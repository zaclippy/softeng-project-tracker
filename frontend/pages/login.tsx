import { Text } from '@mantine/core';

export default function Requirements() {
  return (
    <>
      <form className="form">
        <label htmlFor="user">Enter user to switch to:</label>
        <input type="text" id="user" name="user" />
        <button type="submit">Switch</button>
      </form>
    </>
  );
}
