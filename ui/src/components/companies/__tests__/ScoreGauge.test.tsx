import { render, screen } from "@testing-library/react";
import { test, expect } from "vitest";
import { ScoreGauge } from "../ScoreGauge";

test("renders score value and breakdown bars", () => {
  render(
    <ScoreGauge
      total={73}
      breakdown={{ market: 80, team: 70, moat: 60, traction: 75, fund_fit: 80 }}
    />,
  );
  expect(screen.getByText("73")).toBeInTheDocument();
  expect(screen.getByText("Market")).toBeInTheDocument();
});

test("renders 0 when total is null", () => {
  render(<ScoreGauge total={null} breakdown={null} />);
  expect(screen.getByText("0")).toBeInTheDocument();
});
