import React from "react";

const HowItWorks = () => {
  const steps = [
    {
      step: "1",
      title: "Upload Your Document",
      desc: "Upload a contract, policy, or legal document in PDF or text format."
    },
    {
      step: "2",
      title: "AI Simplification",
      desc: "Our AI processes the text and translates legal jargon into simple terms."
    },
    {
      step: "3",
      title: "Get Easy Explanations",
      desc: "Read the simplified version instantly, broken down by sections and clauses."
    }
  ];

  return (
    <div className="px-6 py-10 max-w-4xl mx-auto">
      <h2 className="text-3xl font-bold mb-6 text-blue-700">How It Works</h2>
      <div className="grid md:grid-cols-3 gap-6">
        {steps.map((item) => (
          <div
            key={item.step}
            className="border rounded-2xl p-6 shadow-md hover:shadow-lg transition bg-white"
          >
            <div className="text-2xl font-bold text-blue-600 mb-2">
              Step {item.step}
            </div>
            <h3 className="text-xl font-semibold mb-2">{item.title}</h3>
            <p className="text-gray-700">{item.desc}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default HowItWorks;
