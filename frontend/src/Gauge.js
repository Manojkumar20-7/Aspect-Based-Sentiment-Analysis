// Gauge.js
import React from "react";
import { CircularProgressbar, buildStyles } from "react-circular-progressbar";
import "react-circular-progressbar/dist/styles.css";

const Gauge = ({ positivePercentage }) => {
  return (
    <div className="gauge">
      <CircularProgressbar
        value={positivePercentage}
        text={`${positivePercentage}%`}
        styles={buildStyles({
          pathColor: `rgba(62, 152, 199, ${positivePercentage / 100})`,
          textColor: "#3e98c7",
          trailColor: "#d6d6d6",
        })}
      />
      <p>Sentiment Percentage</p>
    </div>
  );
};

export default Gauge;
