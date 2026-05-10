import { render, screen } from "@testing-library/react";
import { test, expect } from "vitest";
import { StatusPill } from "../StatusPill";

test("renders ready status", () => {
  render(<StatusPill status="ready" />);
  expect(screen.getByText("ready")).toBeInTheDocument();
});

test("renders generating status", () => {
  render(<StatusPill status="generating" />);
  expect(screen.getByText("generating")).toBeInTheDocument();
});

test("renders failed status", () => {
  render(<StatusPill status="failed" />);
  expect(screen.getByText("failed")).toBeInTheDocument();
});
