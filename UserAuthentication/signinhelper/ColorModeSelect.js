import React from 'react';
import { Switch } from '@mui/material';

const ColorModeSelect = () => {
  const [mode, setMode] = React.useState('light');

  const handleToggle = () => {
    setMode((prevMode) => (prevMode === 'light' ? 'dark' : 'light'));
  };

  return <Switch checked={mode === 'dark'} onChange={handleToggle} />;
};

export default ColorModeSelect;
