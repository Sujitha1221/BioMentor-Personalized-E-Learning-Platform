import { NavLink } from "react-router-dom";

const ActiveLink = ({ to, children }) => {
  return (
    <NavLink
      to={to}
      className={({ isActive }) =>
        `px-3 py-2 text-lg transition duration-300 no-underline ${
          isActive
            ? "text-blue-500 font-bold" // Active color (change if needed)
            : "text-white"
        } hover:text-green-400`
      }
      style={{ textDecoration: "none" }} // Ensure no underline
    >
      {children}
    </NavLink>
  );
};

export default ActiveLink;
