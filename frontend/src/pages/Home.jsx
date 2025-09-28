import React from "react";
import FileUpload from "../components/FileUpload";
import SimplifiedOutput from "../components/SimplifiedOutput";

const Home = () => {
  return (
    <div className="flex flex-col items-center justify-center px-6 py-10 text-center">

      <div className="w-full max-w-2xl">
        <FileUpload />
        <SimplifiedOutput />
      </div>
    </div>
  );
};

export default Home;
