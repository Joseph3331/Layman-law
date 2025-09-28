import React from "react";

const About = () => {
  return (
    <div className="px-6 py-10 max-w-3xl mx-auto">
      <h2 className="text-3xl font-bold mb-4 text-blue-700">About Layman Law</h2>
      <p className="text-gray-700 mb-4">
        Legal documents are often filled with jargon and complex clauses
        that make them hard to understand for the general public. Layman
        Law bridges this gap by using AI to simplify these documents into
        plain, human-friendly explanations.
      </p>
      <p className="text-gray-700 mb-4">
        Our mission is to empower individuals, startups, and small
        businesses to understand their contracts, agreements, and policies
        without needing advanced legal knowledge.
      </p>
      <p className="text-gray-700">
        We believe that everyone deserves access to clarity when it comes
        to legal matters — and that’s exactly what Layman Law provides.
      </p>
    </div>
  );
};

export default About;
