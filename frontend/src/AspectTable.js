// AspectTable.js
import React from "react";

const AspectTable = ({ analysis }) => {
  return (
    <table className="aspect-table">
      <thead>
        <tr>
          <th>Sentence</th>
          <th>Aspects</th>
          <th>Sentiment</th>
          <th>Key Sentiment Words</th>
        </tr>
      </thead>
      <tbody>
        {analysis.map((item, index) => (
          <tr key={index}>
            <td>{item.sentence}</td>
            <td>{item.aspects.join(", ")}</td>
            <td className={item.sentiment.toLowerCase()}>{item.sentiment}</td>
            <td>{item.sentiment_words.join(", ")}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
};

export default AspectTable;
