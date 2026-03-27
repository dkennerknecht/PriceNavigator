import { fireEvent, render, screen } from "@testing-library/react";

import { DataTable } from "@/components/data-table";

const rows = [
  { id: 1, name: "Milwaukee Drill", code: "M18FDD3-0" },
  { id: 2, name: "WAGO Connector", code: "221-413" },
];

describe("DataTable", () => {
  it("filters visible rows with the search input", () => {
    render(
      <DataTable
        title="Products"
        rows={rows}
        getRowKey={(row) => row.id}
        searchableText={(row) => `${row.name} ${row.code}`}
        columns={[
          { key: "name", label: "Name", render: (row) => row.name },
          { key: "code", label: "Code", render: (row) => row.code },
        ]}
      />,
    );

    expect(screen.getByText("Milwaukee Drill")).toBeInTheDocument();
    expect(screen.getByText("WAGO Connector")).toBeInTheDocument();

    fireEvent.change(screen.getByPlaceholderText("Filtern"), {
      target: { value: "wago" },
    });

    expect(screen.queryByText("Milwaukee Drill")).not.toBeInTheDocument();
    expect(screen.getByText("WAGO Connector")).toBeInTheDocument();
  });
});

