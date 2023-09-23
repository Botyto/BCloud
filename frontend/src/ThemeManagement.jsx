import React from 'react';

export const ThemeContext = React.createContext({
	toggleColorMode: () => {},
});

function ThemeManagement(props) {
	const prefersDarkMode = useMediaQuery('(prefers-color-scheme: dark)');
	const [darkTheme, setDarkTheme] = React.useState<'light' | 'dark'>(prefersDarkMode ? 'dark' : 'light');
	const colorTheme = React.useMemo(
		() => ({
			toggleColorMode: () => {
				setDarkTheme((prevTheme) => (prevTheme === 'light' ? 'dark' : 'light'));
			},
		}),
		[],
	);

	const theme = React.useMemo(
		() => createTheme({
			darkTheme,
		}),
		[darkTheme],
	);

	return (
		<ThemeContext.Provider value={colorTheme}>
			{props.children}
		</ThemeContext.Provider>
	);
}

export { ThemeManagement };
