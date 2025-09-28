import React from "react";

const Footer = () => {
  return (
    <footer className="bg-gray-100 text-gray-600 text-center py-6 mt-10 border-t">
      <p className="text-sm">
        © {new Date().getFullYear()} Layman Law. All rights reserved.
      </p>
      <p className="text-xs mt-2">
        Built with ❤️ at Hackathons to make legal documents simpler.
      </p>
    </footer>
  );
};

export default Footer;
