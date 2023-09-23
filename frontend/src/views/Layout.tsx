import React from "react";
import { Outlet } from "react-router-dom";
import NavButton from "../components/NavButton";

export default function Layout() {
	return <>
		<Outlet/>
		<div style={{position: "fixed", bottom: "25px", right: "25px"}}>
			<NavButton/>
		</div>
	</>;
}
