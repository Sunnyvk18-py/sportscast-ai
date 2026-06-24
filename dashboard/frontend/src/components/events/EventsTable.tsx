import {
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  useReactTable,
  type ColumnDef,
} from "@tanstack/react-table";
import { useNavigate } from "react-router-dom";
import type { DetectedEvent } from "@/lib/types";
import { formatPercent, formatTimestamp } from "@/lib/utils";
import EventTypeBadge from "./EventTypeBadge";

interface Props {
  data: DetectedEvent[];
}

export default function EventsTable({ data }: Props) {
  const navigate = useNavigate();

  const columns: ColumnDef<DetectedEvent>[] = [
    {
      accessorKey: "timestamp_ms",
      header: "Time",
      cell: ({ row }) => formatTimestamp(row.original.timestamp_ms),
    },
    {
      accessorKey: "event_type",
      header: "Event Type",
      cell: ({ row }) => <EventTypeBadge type={row.original.event_type} />,
    },
    {
      accessorKey: "composite_confidence",
      header: "Confidence",
      cell: ({ row }) => formatPercent(row.original.composite_confidence),
    },
    {
      accessorKey: "signals_agreed",
      header: "Signals",
      cell: ({ row }) => `${row.original.signals_agreed}/3`,
    },
    {
      id: "status",
      header: "Status",
      cell: ({ row }) =>
        row.original.auto_confirmed
          ? "Confirmed"
          : row.original.requires_review
            ? "Review"
            : "—",
    },
    {
      accessorKey: "commentary",
      header: "Commentary",
      cell: ({ row }) =>
        row.original.commentary
          ? row.original.commentary.slice(0, 40) + (row.original.commentary.length > 40 ? "…" : "")
          : "—",
    },
    {
      accessorKey: "highlight_clip_path",
      header: "Clip",
      cell: ({ row }) => (row.original.highlight_clip_path ? "✓" : "—"),
    },
  ];

  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    initialState: { pagination: { pageSize: 20 } },
  });

  return (
    <div>
      <table className="w-full text-sm">
        <thead>
          {table.getHeaderGroups().map((hg) => (
            <tr key={hg.id} className="border-b border-border text-left text-foreground/60">
              {hg.headers.map((h) => (
                <th
                  key={h.id}
                  className="py-3 px-2 cursor-pointer"
                  onClick={h.column.getToggleSortingHandler()}
                >
                  {flexRender(h.column.columnDef.header, h.getContext())}
                </th>
              ))}
            </tr>
          ))}
        </thead>
        <tbody>
          {table.getRowModel().rows.map((row) => (
            <tr
              key={row.id}
              className="border-b border-border/50 hover:bg-card cursor-pointer"
              onClick={() => navigate(`/events/${row.original.id}`)}
            >
              {row.getVisibleCells().map((cell) => (
                <td key={cell.id} className="py-3 px-2">
                  {flexRender(cell.column.columnDef.cell, cell.getContext())}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
      <div className="flex items-center justify-between mt-4 text-sm text-foreground/60">
        <span>
          Page {table.getState().pagination.pageIndex + 1} of {table.getPageCount()}
        </span>
        <div className="flex gap-2">
          <button
            className="px-3 py-1 rounded border border-border hover:bg-card"
            onClick={() => table.previousPage()}
            disabled={!table.getCanPreviousPage()}
          >
            Prev
          </button>
          <button
            className="px-3 py-1 rounded border border-border hover:bg-card"
            onClick={() => table.nextPage()}
            disabled={!table.getCanNextPage()}
          >
            Next
          </button>
        </div>
      </div>
    </div>
  );
}
