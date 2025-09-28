import React from "react";
import "./Navbar.css";

function Navbar() {
  return (
    <nav className="navbar">
      <div className="navbar-logo">⚖️ Layman Law</div>
      <ul className="navbar-links">
        <li><a href="/">Home</a></li>
        <li><a href="/how-it-works">How It Works</a></li>
        <li><a href="/about">About</a></li>
      </ul>
    </nav>
  );
}

export default Navbar;
