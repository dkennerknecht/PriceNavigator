"use client";

import { useDeferredValue, useState } from "react";

type Column<T> = {
  key: string;
  label: string;
  render: (row: T) => React.ReactNode;
};

type DataTableProps<T> = {
  title: string;
  description?: string;
  rows: T[];
  columns: Column<T>[];
  getRowKey: (row: T) => string | number;
  searchableText?: (row: T) => string;
  emptyMessage?: string;
};

export function DataTable<T>({
  title,
  description,
  rows,
  columns,
  getRowKey,
  searchableText,
  emptyMessage = "Keine Datensätze vorhanden.",
}: DataTableProps<T>) {
  const [query, setQuery] = useState("");
  const deferredQuery = useDeferredValue(query);
  const normalizedQuery = deferredQuery.trim().toLowerCase();

  const visibleRows = rows.filter((row) => {
    if (!normalizedQuery || !searchableText) {
      return true;
    }
    return searchableText(row).toLowerCase().includes(normalizedQuery);
  });

  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          <p className="eyebrow">Datenansicht</p>
          <h2>{title}</h2>
          {description ? <p className="muted">{description}</p> : null}
        </div>
        <label className="search-box">
          <span>Suche</span>
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Filtern"
          />
        </label>
      </div>
      <div className="table-wrap">
        <table className="data-table">
          <thead>
            <tr>
              {columns.map((column) => (
                <th key={column.key}>{column.label}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {visibleRows.length ? (
              visibleRows.map((row) => (
                <tr key={getRowKey(row)}>
                  {columns.map((column) => (
                    <td key={`${getRowKey(row)}-${column.key}`}>{column.render(row)}</td>
                  ))}
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={columns.length}>
                  <div className="empty-state">{emptyMessage}</div>
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}

